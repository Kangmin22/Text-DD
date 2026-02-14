# File: src/systems/combat_system.py
import random
from typing import List, Dict, Any
from src.models.actor import Actor
from src.models.combat_context import CombatContext
from src.systems.math_engine import MathEngine
from src.systems.skill_system import SkillSystem
from src.systems.growth_system import GrowthSystem

class CombatSystem:
    """
    전투의 규칙(Rule)을 집행하는 시스템.
    주도권 계산, 스킬 실행, 방어 판정, 상태 이상 처리 등을 담당함.
    """

    @staticmethod
    def initialize_combat(players: List[Actor], enemies: List[Actor]) -> CombatContext:
        """
        전투를 초기화하고 주도권을 계산하여 CombatContext를 생성합니다.
        """
        ctx = CombatContext(participants=players, enemies=enemies)
        
        # 1. 주도권 결정 (DEX 기반 + 약간의 랜덤)
        all_actors = players + enemies
        # Score = (DEX * 1.5) + (1d20)
        scored_actors = []
        for a in all_actors:
            dex = GrowthSystem.get_scaled_stat(a, "dexterity")
            score = (dex * 1.5) + random.randint(1, 20)
            scored_actors.append((score, a.id))
        
        # 점수 높은 순으로 정렬
        scored_actors.sort(key=lambda x: x[0], reverse=True)
        ctx.turn_order = [x[1] for x in scored_actors]
        
        return ctx

    @staticmethod
    def calculate_hit_chance(attacker: Actor, defender: Actor) -> float:
        """
        기본 명중률 계산 (추후 스킬별 보정치 추가 가능)
        """
        attacker_dex = GrowthSystem.get_scaled_stat(attacker, "dexterity")
        defender_dex = GrowthSystem.get_scaled_stat(defender, "dexterity")
        
        # 기본 90% 명중률 + (공격자 DEX - 방어자 DEX) * 0.5%
        hit_chance = 90 + (attacker_dex - defender_dex) * 0.5
        return max(50, min(100, hit_chance)) # 최소 50%, 최대 100%

    @staticmethod
    def process_action(attacker: Actor, defender: Actor, skill_id: str, ctx: CombatContext):
        """
        스킬 실행, 명중/회피 판정, 데미지 계산 및 적용을 수행하는 핵심 전투 로직.
        """
        # 1. 스킬 데이터 로드 및 1차 데미지 계산 (공격자 스탯 기반)
        res = SkillSystem.calculate_skill_damage(attacker, skill_id)
        
        if "error" in res:
            ctx.add_log(f"⚠️ {attacker.name}: {res['error']}")
            return

        raw_damage = res["damage"]
        skill_name = res["skill_name"]
        cost = res["cost"]

        # 2. 자원 소모 (명중 여부와 상관없이 소모됨)
        attacker.current_mp -= cost.get("mp", 0)
        attacker.current_hp -= cost.get("hp", 0)

        # 3. 회피(Dodge) 판정
        defender_dex = GrowthSystem.get_scaled_stat(defender, "dexterity")
        # 스킬 타입이 물리(physical)일 때만 회피 가능하도록 설정 가능 (현재는 전체 적용)
        if MathEngine.roll_dodge(defender_dex):
            ctx.add_log(f"💨 {attacker.name}의 [{skill_name}]! 그러나 {defender.name}이(가) 날렵하게 피했습니다!")
            return

        # 4. 치명타(Critical) 판정
        attacker_dex = GrowthSystem.get_scaled_stat(attacker, "dexterity")
        is_crit = MathEngine.roll_critical(attacker_dex)

        # 5. 방어력 및 최종 데미지 계산 (MathEngine 위임)
        defender_armor = GrowthSystem.get_scaled_stat(defender, "constitution") * 5
        # TODO: 장비 방어력 합산 로직 추가 필요 (InventorySystem 연동)
        
        final_damage = MathEngine.calculate_final_damage(
            raw_damage=raw_damage,
            armor=defender_armor,
            attacker_level=attacker.level,
            is_crit=is_crit
        )

        # 6. 피해 적용
        defender.current_hp = max(0, defender.current_hp - final_damage)

        # 7. 로그 기록 (상세 정보 포함)
        attack_emoji = "⚔️" if res["type"] == "physical" else "🔮"
        crit_msg = " (치명타!)" if is_crit else ""
        
        # 방어력 감소율 역산 (로그 표시용)
        dr = MathEngine.calculate_defense_dr(defender_armor, attacker.level)
        dr_percent = int(dr * 100)
        
        ctx.add_log(f"{attack_emoji} {attacker.name}의 [{skill_name}]!{crit_msg}")
        ctx.add_log(f"   {defender.name}에게 {final_damage}의 피해! (방어력으로 {dr_percent}% 감소)")

        if defender.current_hp <= 0:
            ctx.add_log(f"💀 {defender.name}가 쓰러졌습니다!")