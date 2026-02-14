# File: src/systems/math_engine.py
import math
import random

class MathEngine:
    """
    게임 내 모든 수치 계산을 담당하는 핵심 엔진.
    공격, 방어, 확률 등의 공식을 중앙에서 관리함.
    """

    @staticmethod
    def calculate_damage_variance(base_damage: int, variance_percent: float = 0.1) -> int:
        """
        기본 데미지에 ±variance_percent 만큼의 랜덤 변동을 줍니다.
        예: 100 데미지, 10% 변동 -> 90 ~ 110 사이의 값 반환
        """
        min_dmg = int(base_damage * (1 - variance_percent))
        max_dmg = int(base_damage * (1 + variance_percent))
        return random.randint(min_dmg, max_dmg)

    @staticmethod
    def calculate_defense_dr(armor: int, attacker_level: int) -> float:
        """
        WoW 스타일 방어력 점감 공식 (Diminishing Returns)
        DR = Armor / (Armor + K)
        K = 레벨 상수 (여기서는 간단히 level * 50 + 100 사용)
        """
        k_constant = (attacker_level * 50) + 100
        dr = armor / (armor + k_constant)
        return min(0.75, dr) # 최대 75% 감소로 제한 (캡)

    @staticmethod
    def roll_critical(attacker_dex: int, base_chance: float = 0.05) -> bool:
        """
        치명타 발생 여부를 판정합니다.
        기본 확률 5% + (DEX * 0.002) (DEX 100당 20% 추가)
        """
        chance = base_chance + (attacker_dex * 0.002)
        return random.random() < chance

    @staticmethod
    def roll_dodge(defender_dex: int, attacker_accuracy: int = 100) -> bool:
        """
        회피 여부를 판정합니다.
        회피율 = (DEX * 0.001) (DEX 100당 10%)
        단, 공격자의 명중률이 높으면 상쇄될 수 있음 (추후 구현)
        """
        dodge_chance = defender_dex * 0.001
        return random.random() < min(0.5, dodge_chance) # 최대 50% 회피율 제한

    @staticmethod
    def calculate_final_damage(raw_damage: int, armor: int, attacker_level: int, is_crit: bool) -> int:
        """
        모든 요소를 종합하여 최종 데미지를 계산합니다.
        1. 방어력 감소 적용
        2. 치명타 배율 적용 (1.5배)
        3. 랜덤 분산 적용
        """
        # 1. 방어력 적용
        dr = MathEngine.calculate_defense_dr(armor, attacker_level)
        damage_after_armor = raw_damage * (1 - dr)

        # 2. 치명타 적용
        if is_crit:
            damage_after_armor *= 1.5

        # 3. 랜덤 분산 적용 (최종적으로 정수 변환)
        final_damage = MathEngine.calculate_damage_variance(int(damage_after_armor))
        
        return max(1, final_damage) # 최소 1 데미지 보장