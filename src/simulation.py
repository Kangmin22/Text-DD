import sys
import os
import statistics
import random
import math
from typing import Dict, List

# --- 경로 설정 수정 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models.actor import Actor
from src.models.combat_context import CombatContext

# --- 🚀 Phase 4: Role-Based Actor ---
class StressTestActor(Actor):
    """
    역할군에 따른 특화 스탯 성장을 지원하는 액터.
    """
    GROWTH_RATE = 0.5

    @property
    def max_hp(self) -> int:
        # [v6.1] TTK 최적화를 위한 HP 보너스 계수 (미세 조정)
        level_bonus = self.level * 2.1 * math.log(self.level + 1)
        return int(20 + (self.base_stats["CON"] * 10) + level_bonus)

    def get_scaled_stats(self) -> Dict[str, int]:
        """Base + Log Scaling"""
        scaled = {}
        for stat, val in self.base_stats.items():
            bonus = val * self.GROWTH_RATE * math.log(self.level + 1)
            scaled[stat] = int(val + bonus)
        return scaled

    @property
    def attack_power(self) -> int:
        stats = self.get_scaled_stats()
        # 기초 파괴력 산출
        return int(stats["STR"] * 2.0 + stats["DEX"] * 0.5)

    @property
    def defense(self) -> int:
        stats = self.get_scaled_stats()
        return int(stats["CON"] * 1.5 + stats["STR"] * 0.2)

    @property
    def accuracy(self) -> int:
        stats = self.get_scaled_stats()
        return stats["DEX"] * 3

    @property
    def evasion(self) -> int:
        stats = self.get_scaled_stats()
        return stats["DEX"] * 2

# --- 🚀 Final Combat Core: Tri-Equilibrium (v6.1 - The Refined Equilibrium) ---
class FinalCombatSystem:
    # 밸런싱 상수
    BASE_CRIT_MULT = 1.5
    MAX_CRIT_MULT = 2.2         # [v6.1] 암살자의 죽창력을 위해 상향
    MAX_CRIT_CHANCE = 0.40      # [v6.1] 상향
    CRIT_CHANCE_FACTOR = 0.015
    EVA_FACTOR = 0.6            # [v6.1] 회피 효율 상향
    REFLECT_CAP = 0.20          # [v6.1] 반사 상한 소폭 상향
    MIN_HIT_CHANCE = 0.65       # [v6.1] 핵심! 최소 명중률을 낮춰서 고DEX 캐릭터의 회피를 실질적으로 보장

    @staticmethod
    def process_turn(context: CombatContext, action: str = "attack") -> dict:
        attacker = context.get_current_attacker()
        defender = context.get_current_defender()
        
        result = {
            "turn": context.turn_count,
            "damage": 0,
            "reflected": 0,
            "is_hit": False,
            "is_crit": False,
            "is_dead": False
        }

        # 보정 스탯 캐싱
        a_stats = attacker.get_scaled_stats() if hasattr(attacker, 'get_scaled_stats') else attacker.base_stats
        d_stats = defender.get_scaled_stats() if hasattr(defender, 'get_scaled_stats') else defender.base_stats

        # --- [Step 1: 명중/회피] ---
        acc = attacker.accuracy
        eva = defender.evasion
        # [v6.1] 최소 명중률(MIN_HIT_CHANCE)이 낮아져서 이제 DEX 빌드가 진짜로 '피합니다'
        hit_chance = max(FinalCombatSystem.MIN_HIT_CHANCE, acc / (acc + (eva * FinalCombatSystem.EVA_FACTOR)))

        if random.random() > hit_chance:
            result["is_hit"] = False
            context.turn_count += 1
            return result

        result["is_hit"] = True

        # --- [Step 2: STR 기반 압도 (Overpower)] ---
        overpower_mult = 1.0 + (a_stats["STR"] / (a_stats["STR"] + 80) * 0.25)

        # --- [Step 3: 데미지 계산 (기본 방어 감쇄)] ---
        atk = attacker.attack_power
        defense_val = defender.defense
        mitigation = atk / (atk + defense_val * 0.65) # 방어 효율 소폭 완화
        raw_damage = atk * mitigation * random.uniform(0.95, 1.05) * overpower_mult

        # --- [Step 4: CON 기반 고유 저항] ---
        con_resilience = d_stats["CON"] / (d_stats["CON"] + 100)
        raw_damage *= (1.0 - con_resilience)

        # --- [Step 5: 크리티컬 (DEX 죽창력 상향)] ---
        crit_prob = min(FinalCombatSystem.MAX_CRIT_CHANCE, a_stats["DEX"] * FinalCombatSystem.CRIT_CHANCE_FACTOR)
        if random.random() < crit_prob:
            crit_mult = FinalCombatSystem.BASE_CRIT_MULT + (a_stats["DEX"] * 0.02)
            raw_damage *= min(FinalCombatSystem.MAX_CRIT_MULT, crit_mult)
            result["is_crit"] = True

        # --- [Step 6: DEX 기반 약점 찌르기 (Penetration Buff)] ---
        # [v6.1] 이제 관통이 CON 저항을 일부 무시하도록 설계
        pen_rate = a_stats["DEX"] / (a_stats["DEX"] + 40)
        raw_damage *= (1.0 + pen_rate)

        # --- [Step 7: 최종 데미지 확정 및 반사 (Weight of Steel)] ---
        # [v6.1] CON 탱커의 결정타 부족 해결: 자신의 방어력의 일부를 공격력에 추가 (보복 데미지)
        vengence_dmg = d_stats["CON"] * 0.5
        final_damage = int(max(1, raw_damage + (vengence_dmg if a_stats["CON"] > a_stats["STR"] else 0)))
        
        # 반사 상한 적용
        raw_reflect = d_stats["CON"] / (d_stats["CON"] + 100)
        reflect_rate = min(FinalCombatSystem.REFLECT_CAP, raw_reflect)
        reflected_dmg = int(final_damage * reflect_rate)
        
        # 결과 적용
        result["damage"] = final_damage
        result["reflected"] = reflected_dmg
        
        defender.current_hp = max(0, defender.current_hp - final_damage)
        attacker.current_hp = max(0, attacker.current_hp - reflected_dmg)
        
        # 승리 판정
        if defender.current_hp <= 0:
            result["is_dead"] = True
            context.is_finished = True
            context.winner = attacker
        elif attacker.current_hp <= 0:
            result["is_dead"] = True
            context.is_finished = True
            context.winner = defender
        else:
            context.turn_count += 1

        return result

# --- 🚀 Professional Simulation Engine ---

def run_simulation(p_stats: dict, e_stats: dict, level: int = 1, battles: int = 100):
    wins = 0
    turn_counts = []
    damages = []
    
    for _ in range(battles):
        p = StressTestActor("p_unit", "Hero", level=level, base_stats=p_stats)
        e = StressTestActor("e_unit", "Mob", level=level, base_stats=e_stats)
        p.current_hp = p.max_hp
        e.current_hp = e.max_hp
        
        ctx = CombatContext(player=p, enemy=e)
        
        while not ctx.is_finished:
            res = FinalCombatSystem.process_turn(ctx)
            if res["is_hit"]:
                damages.append(res["damage"])
            
        if ctx.winner and ctx.winner.id == "p_unit":
            wins += 1
        turn_counts.append(ctx.turn_count)

    avg_dmg = statistics.mean(damages) if damages else 0
    std_dmg = statistics.stdev(damages) if len(damages) > 1 else 0

    return {
        "win_rate": (wins / battles) * 100,
        "avg_turns": statistics.mean(turn_counts),
        "avg_damage": avg_dmg,
        "dmg_cv": (std_dmg / avg_dmg) if avg_dmg > 0 else 0
    }

def perform_stress_tests():
    print("=== 🧪 DYNAMIC STRESS TEST: LEVEL SCALING (v6.1) ===")
    print("-" * 65)
    print(f"{'LV':<4} | {'Win%':<6} | {'TTK(Avg)':<8} | {'AvgDmg':<8} | {'DmgCV':<6}")
    print("-" * 65)
    
    p_stats = {"STR": 16, "DEX": 13, "CON": 15, "INT": 10} 
    e_stats = {"STR": 13, "DEX": 8, "CON": 15, "INT": 5}

    for lv in [1, 10, 20, 30, 40, 50]:
        res = run_simulation(p_stats, e_stats, level=lv, battles=500)
        print(f"{lv:<4} | {res['win_rate']:>5.1f}% | {res['avg_turns']:>8.1f} | {res['avg_damage']:>8.1f} | {res['dmg_cv']:>6.2f}")

    print("\n=== 🧪 EXTREME BUILD TEST: THE REFINED EQUILIBRIUM (LV 20) ===")
    print("목표: DEX(회피 보장) vs CON(보복 데미지) 빌드의 생존력 확인")
    print("-" * 65)
    
    builds = {
        "STR Focus (Berserker)": {"STR": 25, "DEX": 8, "CON": 10, "INT": 5},
        "DEX Focus (Assassin) ": {"STR": 10, "DEX": 25, "CON": 8, "INT": 5},
        "CON Focus (Tanker)   ": {"STR": 10, "DEX": 8, "CON": 25, "INT": 5}
    }
    
    # 엘리트 몹 상정
    e_stats_standard = {"STR": 18, "DEX": 12, "CON": 18, "INT": 10}
    
    for name, stats in builds.items():
        res = run_simulation(stats, e_stats_standard, level=20, battles=1000)
        print(f"[{name}] Win: {res['win_rate']:>5.1f}% | TTK: {res['avg_turns']:>4.1f} | DmgCV: {res['dmg_cv']:>4.2f}")

if __name__ == "__main__":
    perform_stress_tests()