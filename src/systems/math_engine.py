# File: src/systems/math_engine.py
import math

class MathEngine:
    """
    v9.0 시뮬레이션에서 검증된 핵심 수학 공식 라이브러리.
    """
    
    @staticmethod
    def calculate_defense_dr(armor: int, attacker_level: int) -> float:
        """
        WoW Hyperbolic Defense Formula: DR = Armor / (Armor + K)
        K = 400 + 85 * Level
        """
        if armor <= 0: return 0.0
        k_constant = 400 + (85 * attacker_level)
        return armor / (armor + k_constant)

    @staticmethod
    def calculate_hit_chance(accuracy: int, evasion: int, min_chance: float = 0.05, max_chance: float = 1.0) -> float:
        """
        표준 명중률 공식 (Standard Hit Formula)
        """
        if accuracy <= 0: return min_chance
        chance = accuracy / (accuracy + (evasion * 0.5))
        return max(min_chance, min(max_chance, chance))

    @staticmethod
    def log_growth(base: int, level: int, growth_rate: float = 0.5) -> int:
        """
        로그 스케일링 성장 공식: Base + (Base * Rate * log(Level + 1))
        """
        bonus = base * growth_rate * math.log(level + 1)
        return int(base + bonus)

class StatBucket:
    """
    PoE Style Damage Pipeline: Base -> Flat -> Increased -> More
    """
    def __init__(self, base_value: float):
        self.base = base_value
        self.flat = 0.0
        self.increased = 0.0 
        self.more = []       

    def add_flat(self, val: float): self.flat += val
    def add_increased(self, val: float): self.increased += val
    def add_more(self, val: float): self.more.append(val)

    def calculate(self) -> float:
        val = self.base + self.flat
        val *= (1.0 + self.increased)
        for m in self.more:
            val *= m
        return val