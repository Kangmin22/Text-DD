# File: src/systems/growth_system.py
import math
from src.models.actor import Actor

class GrowthSystem:
    """
    캐릭터의 스탯 성장 및 파생 스탯 계산 시스템.
    (장비 보너스 스탯 포함)
    """

    @staticmethod
    def get_max_hp(actor: Actor) -> int:
        """
        HP 공식: 100 + (CON * 25) + (Level * 8.0 * log(Level + 1))
        * CON은 장비 보너스가 포함된 최종 스탯을 사용해야 함.
        """
        # 여기서 get_scaled_stat을 호출하면 장비빨 CON이 적용됨
        con = GrowthSystem.get_scaled_stat(actor, "constitution")
        level_bonus = actor.level * 8.0 * math.log(actor.level + 1)
        return int(100 + (con * 25) + level_bonus)

    @staticmethod
    def get_scaled_stat(actor: Actor, stat_name: str) -> int:
        """
        최종 스탯 = (베이스 스탯 + 성장 보너스) + 장비 보너스
        """
        stat_key = stat_name.lower()
        base = actor.base_stats.get(stat_key, 10)
        
        # 1. 레벨 성장 보너스
        growth_bonus = base * 0.5 * math.log(actor.level + 1)
        
        # 2. 장비 보너스 합산 (New!)
        equip_bonus = 0
        for slot, item in actor.equipment.items():
            if item: # 장착된 아이템이 있다면
                # item은 dict가 아니라 Item 객체여야 함 (Factory에서 객체화 필요)
                # 안전하게 getattr나 .bonus_stats 접근
                if hasattr(item, "bonus_stats"):
                    equip_bonus += item.bonus_stats.get(stat_key, 0)

        return int(base + growth_bonus + equip_bonus)
    
    @staticmethod
    def refresh_stats(actor: Actor):
        actor.max_hp = GrowthSystem.get_max_hp(actor)
        if actor.current_hp == 0:
            actor.current_hp = actor.max_hp
        # 장착/해제 시 현재 체력이 최대 체력을 넘지 않도록 조정
        if actor.current_hp > actor.max_hp:
            actor.current_hp = actor.max_hp