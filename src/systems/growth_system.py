import math
import random
from src.models.actor import Actor

class GrowthSystem:
    """
    캐릭터 및 몬스터의 성장 수치와 파생 능력치를 계산하는 핵심 엔진.
    Version: v2.2 (Final Balanced - 시뮬레이션 검증 완료)
    
    [설계 변경 로그]
    - TTK(Time To Kill) 확보를 위해 HP 공식 상향 유지.
    - 공격력(AP/SP) 계수를 상향하여 시뮬레이션의 x1.5 보정 효과를 공식에 내장.
    - 레벨업 시 MP 증가폭을 늘려 스킬 활용도 개선.
    """
    
    PRIMARY_STATS = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

    @staticmethod
    def _recalc_stats(actor: Actor):
        """기본 스탯에 레벨 보정과 장비 보너스를 합산하여 캐시를 생성합니다."""
        new_cache = {}
        
        for stat_key in GrowthSystem.PRIMARY_STATS:
            base = actor.base_stats.get(stat_key, 10)
            # 레벨당 기본 스탯 성장 (기존 1.5 유지)
            growth_bonus = (actor.level - 1) * 1.5 
            new_cache[stat_key] = int(base + growth_bonus)

        # 착용 중인 모든 장비의 보너스 스탯 합산
        for item in actor.equipment.values():
            if item and hasattr(item, "bonus_stats"):
                for stat, bonus in item.bonus_stats.items():
                    stat_key = stat.lower()
                    if stat_key in new_cache:
                        new_cache[stat_key] += bonus
                    else:
                        new_cache[stat_key] = bonus

        actor._cached_stats = new_cache
        actor._is_stats_dirty = False

    @staticmethod
    def get_scaled_stat(actor: Actor, stat_name: str) -> int:
        """Dirty Flag가 켜져 있으면 재계산 후 최신 스탯을 반환합니다."""
        if actor._is_stats_dirty:
            GrowthSystem._recalc_stats(actor)
        return actor._cached_stats.get(stat_name.lower(), 0)

    # --------------------------------------------------------------------------
    # [Final Balancing] 전투 수식 - 시뮬레이션 기반 최종값
    # --------------------------------------------------------------------------

    @staticmethod
    def get_max_hp(actor: Actor) -> int:
        """
        HP 공식: (CON * 15) + (Level * 30)
        - 묵직한 체력을 제공하여 전투가 6~12턴 정도 긴장감 있게 유지되도록 함.
        """
        con = GrowthSystem.get_scaled_stat(actor, "constitution")
        return int((con * 15) + (actor.level * 30))

    @staticmethod
    def get_attack_power(actor: Actor) -> int:
        """
        물리 공격력(AP) 공식: (STR + (Level * 3)) * 1.2
        - 시뮬레이션의 Lethality Boost를 공식에 반영.
        - 힘 스탯과 레벨의 가치를 동시에 높임.
        """
        strength = GrowthSystem.get_scaled_stat(actor, "strength")
        base_atk = strength + (actor.level * 3)
        return int(base_atk * 1.2)

    @staticmethod
    def get_magic_power(actor: Actor) -> int:
        """
        주문 공격력(SP) 공식: (INT + (Level * 3)) * 1.2
        - 마법형 캐릭터가 지능 스탯에 투자할 확실한 이유를 제공함.
        """
        intelligence = GrowthSystem.get_scaled_stat(actor, "intelligence")
        base_matk = intelligence + (actor.level * 3)
        return int(base_matk * 1.2)
    
    @staticmethod
    def get_evasion(actor: Actor) -> float:
        """
        회피율 계산 (최대 50%)
        - DEX 10 기준 0%, DEX 30 기준 20%.
        """
        dex = GrowthSystem.get_scaled_stat(actor, "dexterity")
        evasion_chance = max(0, (dex - 10) * 0.01)
        return min(0.5, evasion_chance)

    @staticmethod
    def get_defense(actor: Actor) -> float:
        """
        피해 감소율 계산 (최대 60%)
        - CON 10 기준 0%, CON 30 기준 20%.
        - 갑옷 시스템이 추가되면 이 수치에 합산될 예정.
        """
        con = GrowthSystem.get_scaled_stat(actor, "constitution")
        dr = max(0, (con - 10) * 0.01)
        return min(0.6, dr)

    @staticmethod
    def refresh_stats(actor: Actor):
        """캐릭터의 모든 실시간 능력치(HP, MP 등)를 최신 상태로 갱신합니다."""
        actor.mark_dirty() 
        actor.max_hp = GrowthSystem.get_max_hp(actor)
        
        # MP 공식 상향: 기본 20 + 지혜 보정 + 레벨당 5씩 증가
        wisdom_bonus = GrowthSystem.get_scaled_stat(actor, "wisdom") // 2
        actor.max_mp = 20 + wisdom_bonus + (actor.level * 5)
        
        # 사망 상태가 아니면 현재 체력이 최대치를 넘지 않도록 보정
        if actor.current_hp <= 0 or actor.current_hp > actor.max_hp: 
            actor.current_hp = actor.max_hp
            
        actor.current_mp = min(actor.current_mp, actor.max_mp)