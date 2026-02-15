from src.models.actor import Actor
from src.models.combat_context import CombatContext
from src.utils.data_loader import DataLoader
from src.systems.math_engine import MathEngine
import random

class CombatSystem:
    """
    전투의 흐름(턴, 액션, 결과)을 제어하는 핵심 시스템.
    Version: v2.2 (시뮬레이션 기반 최종 밸런스 적용)
    
    [주요 기능]
    - 주도권(DEX 기반) 계산 및 턴 순서 결정.
    - 스킬 데이터 기반 MP 소모 및 데미지 계산 처리.
    - 매 액션 종료 후 MP 소량 회복 (전투 유지력 확보).
    """

    @staticmethod
    def initialize_combat(players: list, enemies: list) -> CombatContext:
        """
        전투 컨텍스트를 생성하고 주도권(Initiative)을 결정합니다.
        공식: (DEX * 1.5) + 1d20
        """
        ctx = CombatContext(players, enemies)
        
        # 주도권 계산을 위해 모든 참여자 취합
        all_participants = players + enemies
        initiatives = []
        
        # 순환 참조 방지를 위한 지역 임포트
        from src.systems.growth_system import GrowthSystem 
        
        for actor in all_participants:
            dex = GrowthSystem.get_scaled_stat(actor, "dexterity")
            # 주사위 눈금(1~20)을 더해 난수성 부여
            score = (dex * 1.5) + random.randint(1, 20)
            initiatives.append((score, actor.id))
            
        # 점수가 높은 순서대로 정렬하여 턴 순서 확정
        initiatives.sort(key=lambda x: x[0], reverse=True)
        ctx.turn_order = [x[1] for x in initiatives]
        
        return ctx

    @staticmethod
    def process_action(attacker: Actor, defender: Actor, skill_id: str, ctx: CombatContext):
        """
        공격자가 방어자에게 특정 기술을 시전하는 과정을 처리합니다.
        과정: 기술 로드 -> MP 검사 -> 명중 판정 -> 피해 계산 -> 적용 -> 마나 회복
        """
        # 1. 기술 데이터 로드
        skill = DataLoader.load_skill(skill_id)
        if not skill:
            ctx.add_log(f"⚠️ {attacker.name}: 알 수 없는 기술({skill_id})입니다.")
            return

        skill_name = skill.get("name", "Unknown Skill")
        
        # 2. 마나(MP) 소모 체크
        costs = skill.get("cost", {})
        mp_cost = costs.get("mp", 0)
        
        if attacker.current_mp < mp_cost:
            ctx.add_log(f"💧 {attacker.name}: 마력이 부족합니다! ({skill_name} 필요 MP: {mp_cost})")
            return

        # 자원 차감
        attacker.current_mp -= mp_cost

        # 3. 명중 판정 (MathEngine 위임)
        if not MathEngine.roll_hit(attacker, defender, skill):
            ctx.add_log(f"💨 {attacker.name}의 [{skill_name}]! ...하지만 {defender.name}이(가) 피했습니다.")
        else:
            # 4. 데미지 계산 및 적용
            # MathEngine.calculate_skill_damage는 (damage, is_crit) 튜플을 반환함
            result = MathEngine.calculate_skill_damage(attacker, defender, skill)
            
            # 호환성 처리 (튜플이 아닐 경우 대비)
            if isinstance(result, tuple):
                damage, is_crit = result
            else:
                damage = result
                is_crit = False
            
            # 실제 체력 차감
            defender.current_hp = max(0, defender.current_hp - damage)
            
            # 5. 결과 로그 기록
            skill_type = skill.get("type", "physical")
            # 타입에 따른 아이콘 설정
            if skill_type == "physical": icon = "⚔️"
            elif skill_type == "magic": icon = "✨"
            else: icon = "🔮" # Hybrid or Other
            
            crit_text = " (치명타!)" if is_crit else ""
            ctx.add_log(f"{icon} {attacker.name}의 [{skill_name}]!{crit_text} {defender.name}에게 {damage} 피해.")

        # 6. [전략적 포인트] 턴 종료 시 마나 자연 회복
        # 시뮬레이션에서 검증된 '매 턴 2 회복'을 적용하여 스킬 빈도를 높임
        attacker.current_mp = min(attacker.max_mp, attacker.current_mp + 2)

        # 7. 사망 판정
        if defender.current_hp <= 0:
            ctx.add_log(f"💀 {defender.name}이(가) 쓰러졌습니다!")