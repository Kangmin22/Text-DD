# File: src/systems/growth_system.py
import math
from src.models.actor import Actor

class GrowthSystem:
    """
    캐릭터의 비선형 성장 및 파생 능력치를 계산하는 수학 엔진.
    Version: v15.0 (Dirty Flag Caching Optimization Applied)
    """
    
    # 관리 대상 주요 스탯 목록
    PRIMARY_STATS = ["strength", "dexterity", "constitution", "intelligence", "wisdom"]

    @staticmethod
    def _recalc_stats(actor: Actor):
        """
        [최적화] Dirty 상태일 때 호출되어 모든 스탯을 일괄 계산하고 캐시합니다.
        기존의 '요청 시마다 장비 순회' 방식을 '이벤트 발생 시 1회 순회'로 변경합니다.
        """
        # 1. Base + Level Growth 계산
        new_cache = {}
        
        for stat_key in GrowthSystem.PRIMARY_STATS:
            base = actor.base_stats.get(stat_key, 0)
            # 로그 성장 (Base * 0.5 * ln(Lv+1))
            growth_bonus = base * 0.5 * math.log(actor.level + 1)
            new_cache[stat_key] = base + growth_bonus

        # 2. 장비 보너스 합산 (아이템을 한 번만 순회하여 모든 스탯 처리)
        for item in actor.equipment.values():
            if item and hasattr(item, "bonus_stats"):
                for stat, bonus in item.bonus_stats.items():
                    stat_key = stat.lower()
                    # 캐시에 없으면(예: 서브 스탯) 0으로 초기화 후 합산
                    new_cache[stat_key] = new_cache.get(stat_key, 0) + bonus

        # 3. 정수화 및 캐시 적용
        for k, v in new_cache.items():
            new_cache[k] = int(v)
            
        actor._cached_stats = new_cache
        actor._is_stats_dirty = False
        # 디버그용 로그 (필요시 주석 해제)
        # print(f"[DEBUG] Stats recalculated for {actor.name}")

    @staticmethod
    def get_scaled_stat(actor: Actor, stat_name: str) -> int:
        """
        최종 스탯을 반환합니다. (Lazy Evaluation)
        Dirty 상태면 재계산하고, 아니면 캐시된 값을 즉시 반환합니다.
        """
        if actor._is_stats_dirty:
            GrowthSystem._recalc_stats(actor)
            
        return actor._cached_stats.get(stat_name.lower(), 0)

    @staticmethod
    def get_max_hp(actor: Actor) -> int:
        """HP 공식: (CON * 40) + (Level * 5.0 * log(Level + 1))"""
        # get_scaled_stat 내부에서 캐싱 처리됨
        con = GrowthSystem.get_scaled_stat(actor, "constitution")
        level_bonus = actor.level * 5.0 * math.log(actor.level + 1)
        return int(50 + (con * 40) + level_bonus)

    @staticmethod
    def get_max_mp(actor: Actor) -> int:
        """MP 공식: (WIS^2 / 5.5)"""
        wis = GrowthSystem.get_scaled_stat(actor, "wisdom")
        mp_from_wis = (wis ** 2) / 5.5
        return int(max(20, mp_from_wis))

    @staticmethod
    def get_attack_power(actor: Actor) -> int:
        """AP: (STR * 2.5) + (DEX * 0.5) + Level Scaling"""
        strength = GrowthSystem.get_scaled_stat(actor, "strength")
        dexterity = GrowthSystem.get_scaled_stat(actor, "dexterity")
        return int((strength * 2.5) + (dexterity * 0.5) + (actor.level * 2))

    @staticmethod
    def get_magic_power(actor: Actor) -> int:
        """SP: (INT^1.5 / 2.0) + (WIS * 0.8)"""
        intelligence = GrowthSystem.get_scaled_stat(actor, "intelligence")
        wisdom = GrowthSystem.get_scaled_stat(actor, "wisdom")
        return int((intelligence ** 1.5 / 2.0) + (wisdom * 0.8))
    
    @staticmethod
    def refresh_stats(actor: Actor):
        """
        레벨업이나 장비 변경 후 호출되어 리소스 최대치를 갱신합니다.
        이 함수가 호출된다는 것은 상태가 변했다는 뜻이므로 Dirty Flag를 켭니다.
        """
        actor.mark_dirty() # 강제 갱신 트리거
        
        actor.max_hp = GrowthSystem.get_max_hp(actor)
        actor.max_mp = GrowthSystem.get_max_mp(actor)
        
        if actor.current_hp <= 0: actor.current_hp = actor.max_hp
        actor.current_hp = min(actor.current_hp, actor.max_hp)
        
        if actor.current_mp <= 0: actor.current_mp = actor.max_mp
        actor.current_mp = min(actor.current_mp, actor.max_mp)