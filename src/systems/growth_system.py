# File: src/systems/growth_system.py
import math
from src.models.actor import Actor

class GrowthSystem:
    """
    캐릭터의 스탯 성장 및 파생 능력치 계산 시스템.
    (v14.0: MP 공식을 Wisdom 기반으로 분리하여 Specialist Dominance 억제)
    """

    @staticmethod
    def get_max_hp(actor: Actor) -> int:
        """HP: (CON * 40) + Level 보너스"""
        con = GrowthSystem.get_scaled_stat(actor, "constitution")
        level_bonus = actor.level * 5.0 * math.log(actor.level + 1)
        return int(50 + (con * 40) + level_bonus)

    @staticmethod
    def get_max_mp(actor: Actor) -> int:
        """
        MP 공식 변경 (v14.0): (WIS^2 / 5.5)
        - 이제 마나 통은 지능(INT)이 아닌 지혜(WIS)에 의존합니다.
        - 이를 통해 엘프(고지능)가 화력과 자원을 모두 독식하는 것을 방지합니다.
        - 인간(고지혜)이 'Mana Well'로서의 정체성을 가집니다.
        """
        wisdom = GrowthSystem.get_scaled_stat(actor, "wisdom")
        mp_from_wis = (wisdom ** 2) / 5.5
        return int(max(20, mp_from_wis))

    @staticmethod
    def get_attack_power(actor: Actor) -> int:
        """AP: (STR * 2.5) + (DEX * 0.5) + (Level * 2)"""
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
    def get_scaled_stat(actor: Actor, stat_name: str) -> int:
        """최종 스탯 계산 (로그 성장)"""
        stat_key = stat_name.lower()
        base = actor.base_stats.get(stat_key, 10)
        growth_bonus = base * 0.5 * math.log(actor.level + 1)
        
        equip_bonus = 0
        for slot, item in actor.equipment.items():
            if item and hasattr(item, "bonus_stats"):
                equip_bonus += item.bonus_stats.get(stat_key, 0)

        return int(base + growth_bonus + equip_bonus)
    
    @staticmethod
    def refresh_stats(actor: Actor):
        actor.max_hp = GrowthSystem.get_max_hp(actor)
        actor.max_mp = GrowthSystem.get_max_mp(actor)
        actor.current_hp = min(actor.current_hp if actor.current_hp > 0 else actor.max_hp, actor.max_hp)
        actor.current_mp = min(actor.current_mp if actor.current_mp > 0 else actor.max_mp, actor.max_mp)