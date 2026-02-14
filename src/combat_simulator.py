import math
import random
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# =================================================================
# 1. Mathematical Core (Based on Uploaded Documents)
# =================================================================

class MathEngine:
    """
    업로드된 문서(WoW Defense, PoE Pipelines)의 핵심 공식을 구현한 엔진.
    """
    @staticmethod
    def calculate_defense_dr(armor: int, attacker_level: int) -> float:
        """
        WoW Hyperbolic Defense Formula: DR = Armor / (Armor + K)
        K = 400 + 85 * Level (문서 기준 상수)
        """
        k_constant = 400 + (85 * attacker_level)
        if armor <= 0: return 0.0
        return armor / (armor + k_constant)

    @staticmethod
    def calculate_hit_chance(accuracy: int, evasion: int, min_chance: float = 0.05, max_chance: float = 1.0) -> float:
        """
        Standard Hit Formula: Acc / (Acc + Eva)^Entropy
        여기서는 PoE 스타일의 엔트로피 대신 표준 명중 공식 사용.
        """
        if accuracy <= 0: return min_chance
        chance = accuracy / (accuracy + (evasion * 0.5)) # 회피 효율 0.5 계수 적용
        return max(min_chance, min(max_chance, chance))

class StatBucket:
    """
    PoE Style Damage Pipeline:
    Base -> Flat -> Increased(Sum) -> More(Product)
    """
    def __init__(self, base_value: float):
        self.base = base_value
        self.flat = 0.0
        self.increased = 0.0 # 합연산 (예: 0.5 = 50% 증가)
        self.more = []       # 곱연산 (예: 1.5 = 50% 증폭)

    def add_flat(self, val: float): self.flat += val
    def add_increased(self, val: float): self.increased += val
    def add_more(self, val: float): self.more.append(val)

    def calculate(self) -> float:
        # Step 1 & 2: Base + Flat
        val = self.base + self.flat
        # Step 3: Increased (Additive)
        val *= (1.0 + self.increased)
        # Step 4: More (Multiplicative)
        for m in self.more:
            val *= m
        return val

# =================================================================
# 2. Actor Model & Keystones
# =================================================================

@dataclass
class Actor:
    id: str
    name: str
    level: int = 20
    strength: int = 10  # [Fix] str -> strength (내장 타입 shadowing 방지)
    dex: int = 10
    con: int = 10
    current_hp: int = 0
    
    # 키스톤 (Mastery) 활성화 여부
    keystones: Dict[str, bool] = field(default_factory=lambda: {
        "RESOLUTE_TECHNIQUE": False, # STR: 필중 / 노크리
        "DEADLY_ARTS": False,        # DEX: 크리 상한 해제 / 받피증
        "IRON_FORTRESS": False       # CON: 회피 불가 / 받피감 & 반사
    })

    def get_max_hp(self) -> int:
        # HP 스케일 (v8.0 유지)
        level_bonus = self.level * 8.0 * math.log(self.level + 1)
        return int(100 + (self.con * 25) + level_bonus)

    def get_stat(self, name: str) -> int:
        # 스탯 성장 공식 (로그 스케일링)
        base = getattr(self, name.lower())
        bonus = base * 0.5 * math.log(self.level + 1)
        return int(base + bonus)

    def update_keystones(self):
        """스탯 20 이상일 때 해당 특화 키스톤 자동 활성화"""
        raw_str = getattr(self, 'strength')
        raw_dex = getattr(self, 'dex')
        raw_con = getattr(self, 'con')
        
        self.keystones["RESOLUTE_TECHNIQUE"] = raw_str >= 20
        self.keystones["DEADLY_ARTS"] = raw_dex >= 20
        self.keystones["IRON_FORTRESS"] = raw_con >= 20

# =================================================================
# 3. Combat System (v9.0 - The Theoretical Foundation)
# =================================================================

class CombatSystem:
    # 글로벌 밸런스 상수
    BASE_CRIT_MULT = 1.5
    CRIT_CHANCE_PER_DEX = 0.012
    GLOBAL_DMG_SCALE = 0.50

    @staticmethod
    def resolve_round(attacker: Actor, defender: Actor, turn: int) -> dict:
        # 1. 스탯 준비
        str_a = attacker.get_stat("strength")
        dex_a = attacker.get_stat("dex")
        
        str_d = defender.get_stat("strength")
        dex_d = defender.get_stat("dex")
        con_d = defender.get_stat("con")

        # ---------------------------------------------------
        # [Step 1] 명중 판정 (Hit Chance)
        # ---------------------------------------------------
        is_hit = False
        
        # [Keystone: RESOLUTE_TECHNIQUE] (STR)
        # "공격이 빗나가지 않지만, 치명타가 발생하지 않는다."
        if attacker.keystones["RESOLUTE_TECHNIQUE"]:
            is_hit = True
        # [Keystone: IRON_FORTRESS] (CON Defender)
        # "회피할 수 없다."
        elif defender.keystones["IRON_FORTRESS"]:
            is_hit = True
        else:
            acc = dex_a * 4 + str_a * 1 # STR도 명중 기여
            eva = dex_d * 4
            hit_prob = MathEngine.calculate_hit_chance(acc, eva, min_chance=0.60)
            is_hit = random.random() < hit_prob

        if not is_hit:
            return {"hit": False, "crit": False, "dmg": 0, "reflect": 0}

        # ---------------------------------------------------
        # [Step 2] 공격력 산출 (StatBucket Pipeline)
        # ---------------------------------------------------
        # Base: 무기 공격력 (레벨 기반 추정) + 스탯 기여
        weapon_base = attacker.level * 5
        stat_base = (str_a * 2.5) + (dex_a * 1.0)
        
        bucket = StatBucket(weapon_base + stat_base)

        # [Keystone: RESOLUTE_TECHNIQUE] More Damage 30% (안정적 딜링)
        if attacker.keystones["RESOLUTE_TECHNIQUE"]:
            bucket.add_more(1.30)

        # [Keystone: DEADLY_ARTS] (DEX)
        # 관통력 구현: DEX 비례 More 데미지 (방어 계산 전 딜 증폭)
        if attacker.keystones["DEADLY_ARTS"]:
            # DEX 100 기준 약 50% 증폭
            pen_mult = 1.0 + (dex_a / (dex_a + 100)) 
            bucket.add_more(pen_mult)

        raw_dmg = bucket.calculate() * CombatSystem.GLOBAL_DMG_SCALE

        # ---------------------------------------------------
        # [Step 3] 방어 및 피해 감소 (WoW Formula)
        # ---------------------------------------------------
        # Armor 산출: CON이 메인, STR/DEX 보조
        armor = (con_d * 2.0) + (str_d * 0.5) + (dex_d * 0.2)
        
        # [Keystone: IRON_FORTRESS] 방어력 50% 증폭 (More Armor)
        if defender.keystones["IRON_FORTRESS"]:
            armor *= 1.5

        # DR 계산 (Hyperbolic)
        dr = MathEngine.calculate_defense_dr(armor, attacker.level)
        
        # [Keystone: IRON_FORTRESS] 추가 피해 감폭 10% (Flat Reduction이 아닌 %감소)
        mitigation_mult = (1.0 - dr)
        if defender.keystones["IRON_FORTRESS"]:
            mitigation_mult *= 0.90

        actual_dmg = raw_dmg * mitigation_mult

        # ---------------------------------------------------
        # [Step 4] 치명타 (Critical)
        # ---------------------------------------------------
        is_crit = False
        
        # [Keystone: RESOLUTE_TECHNIQUE] 치명타 불가
        can_crit = not attacker.keystones["RESOLUTE_TECHNIQUE"]
        
        if can_crit:
            crit_chance = dex_a * CombatSystem.CRIT_CHANCE_PER_DEX
            # 캡 적용: DEADLY_ARTS는 80%, 아니면 35%
            crit_cap = 0.80 if attacker.keystones["DEADLY_ARTS"] else 0.35
            crit_chance = min(crit_cap, crit_chance)

            if random.random() < crit_chance:
                is_crit = True
                crit_dmg_mult = CombatSystem.BASE_CRIT_MULT
                # DEX 보너스: DEX가 높으면 치명타 피해량 증가
                crit_dmg_mult += (dex_a * 0.01)
                actual_dmg *= crit_dmg_mult

        # ---------------------------------------------------
        # [Step 5] 반사 (Reflect) & 피해 적용
        # ---------------------------------------------------
        final_dmg = int(max(1, actual_dmg))
        reflect_dmg = 0

        # [Keystone: IRON_FORTRESS] 받은 피해의 25% 반사
        if defender.keystones["IRON_FORTRESS"]:
            reflect_dmg = int(final_dmg * 0.25)
        
        # [Keystone: DEADLY_ARTS] 받는 피해 15% 증가 패널티 (Glass Cannon)
        if defender.keystones["DEADLY_ARTS"]:
            final_dmg = int(final_dmg * 1.15)

        # 상태 적용
        defender.current_hp -= final_dmg
        attacker.current_hp -= reflect_dmg

        # IRON_FORTRESS 재생 (턴당 MaxHP 3%)
        if defender.keystones["IRON_FORTRESS"] and defender.current_hp > 0:
            defender.current_hp += int(defender.get_max_hp() * 0.03)

        return {
            "hit": True,
            "crit": is_crit,
            "dmg": final_dmg,
            "reflect": reflect_dmg
        }

# =================================================================
# 4. Simulation Runner
# =================================================================

def run_simulation():
    # 설정: 레벨 20 기준 (중반부 밸런스)
    LEVEL = 20
    BATTLES = 500
    
    # 적 스탯 (밸런스형 엘리트)
    enemy_stats = {"strength": 18, "dex": 15, "con": 18}

    # 테스트할 플레이어 빌드
    builds = [
        ("Berserker (STR 25)", {"strength": 25, "dex": 8, "con": 10}),
        ("Assassin  (DEX 25)", {"strength": 10, "dex": 25, "con": 8}),
        ("Tanker    (CON 25)", {"strength": 10, "dex": 8, "con": 25}),
        ("Balanced  (15/15/15)", {"strength": 15, "dex": 15, "con": 15})
    ]

    print(f"=== [v9.0 Theoretical Foundation Simulation (Lv.{LEVEL})] ===")
    print(f"{'Class':<15} | {'Win%':<6} | {'TTK':<5} | {'Hit%':<6} | {'Crit%':<6} | {'AvgDmg':<8} | {'Reflect':<6}")
    print("-" * 80)

    for name, stats in builds:
        wins = 0
        total_turns = 0
        p_hits = 0
        p_attempts = 0
        p_crits = 0
        p_damages = []
        p_reflects = []

        for _ in range(BATTLES):
            p = Actor("P", "Hero", LEVEL, **stats)
            e = Actor("E", "Enemy", LEVEL, **enemy_stats)
            p.update_keystones() # 키스톤 활성화
            e.update_keystones() # 적은 스탯 낮아서 활성화 안됨 (밸런스형)
            
            p.current_hp = p.get_max_hp()
            e.current_hp = e.get_max_hp()

            turn = 0
            while p.current_hp > 0 and e.current_hp > 0 and turn < 100:
                turn += 1
                
                # Player Turn
                res_p = CombatSystem.resolve_round(p, e, turn)
                p_attempts += 1
                if res_p["hit"]: 
                    p_hits += 1
                    p_damages.append(res_p["dmg"])
                    p_reflects.append(res_p["reflect"])
                    if res_p["crit"]: p_crits += 1
                
                if e.current_hp <= 0:
                    wins += 1
                    break
                
                if p.current_hp <= 0: break

                # Enemy Turn
                res_e = CombatSystem.resolve_round(e, p, turn)
                
            total_turns += turn

        win_rate = (wins / BATTLES) * 100
        avg_ttk = total_turns / BATTLES
        hit_rate = (p_hits / p_attempts * 100) if p_attempts > 0 else 0
        crit_rate = (p_crits / p_hits * 100) if p_hits > 0 else 0
        avg_dmg = statistics.mean(p_damages) if p_damages else 0
        avg_ref = statistics.mean(p_reflects) if p_reflects else 0
        
        print(f"{name:<15} | {win_rate:>5.1f}% | {avg_ttk:>5.1f} | {hit_rate:>5.1f}% | {crit_rate:>5.1f}% | {avg_dmg:>8.1f} | {avg_ref:>6.1f}")

if __name__ == "__main__":
    run_simulation()