# File: src/tests/sim_full_matrix.py
import sys
import os
import math

# 프로젝트 루트 경로 추가
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.factory import EntityFactory
from src.systems.growth_system import GrowthSystem
from src.systems.skill_system import SkillSystem
from src.utils.data_loader import DataLoader

# --- 밸런스 실패 임계값 (Thresholds) ---
MIN_CLASS_AP_GAP_PERCENT = 15.0  # 전사 vs 도적의 AP 차이는 최소 15% 이상이어야 함
MAX_DOMINANCE_SCORE = 2         # 한 조합이 최고 기록(HP, MP, SP, DMG)을 3개 이상 차지하면 실패
TARGET_TTK_MIN = 3              # 동급 전투 시 최소 턴 수 (너무 순삭 방지)
TARGET_TTK_MAX = 8              # 동급 전투 시 최대 턴 수 (지루함 방지)
GEAR_SCALING_FACTOR = 1.5       # 장비 장착 시 스탯 인플레이션 가중치

def run_full_matrix_simulation():
    """
    모든 조합을 조사하고, 자동화된 밸런스 감사(Audit)를 수행하는 마스터 시뮬레이션 (v13.0).
    추가 기능: 장비 스케일링 영향력 테스트, 레벨별 곡선 체크.
    """
    print("=" * 125)
    print(f"{'🧪 [TDD] Race x Class Deep Balance Audit (v13.0)':^125}")
    print("=" * 125)

    r_data = DataLoader.load_json("races.json")
    c_data = DataLoader.load_json("classes.json")
    
    races = r_data.keys()
    classes = c_data.keys()
    
    matrix_results = []
    dominance_tracker = { f"{r}_{c}": 0 for r in races for c in classes }

    # 헤더
    header = f"{'Combination':<18} | {'Lv':<3} | {'HP':<6} | {'MP':<6} | {'AP':<5} | {'SP':<5} | {'TTK':<5} | {'Gear AP':<7} | {'Sig Skill'}"
    print(header)
    print("-" * 125)

    for r_id in races:
        for c_id in classes:
            class_info = c_data[c_id]
            sig_skill = class_info["initial_skills"][0] if class_info["initial_skills"] else "power_strike"

            # 레벨별 곡선 체크를 위해 Lv.1, 25, 50 샘플링
            for level in [1, 25, 50]:
                player = EntityFactory.create_player(f"{r_id}_{c_id}", r_id, c_id)
                player.level = level
                GrowthSystem.refresh_stats(player)

                hp = player.max_hp
                mp = player.max_mp
                ap = GrowthSystem.get_attack_power(player)
                sp = GrowthSystem.get_magic_power(player)
                
                # [Next Step] 장비 스케일링 시뮬레이션: 후반부 아이템이 붙었을 때 AP 격차
                gear_ap = ap * (1.2 if level == 50 else 1.0) # 가상의 장비 보너스
                
                skill_res = SkillSystem.calculate_skill_damage(player, sig_skill)
                dmg = skill_res.get("damage", 0)
                ttk = hp / dmg if dmg > 0 else 99

                res_entry = {
                    "key": f"{r_id}_{c_id}", "race": r_id, "class": c_id, "lv": level,
                    "hp": hp, "mp": mp, "ap": ap, "sp": sp, "dmg": dmg, "ttk": ttk,
                    "gear_ap": gear_ap
                }
                matrix_results.append(res_entry)

                if level == 50:
                    comb_str = f"{r_id.capitalize()} {c_id.capitalize()}"
                    print(f"{comb_str:<18} | {level:<3} | {hp:6d} | {mp:6d} | {ap:5d} | {sp:5d} | {ttk:5.1f} | {gear_ap:7.0f} | {dmg:4d}")

    # --- 밸런스 감사 리포트 (Audit Report) ---
    print("\n" + "=" * 125)
    print(f"{'📊 AUTOMATED BALANCE AUDIT REPORT (Deep Analysis Mode)':^125}")
    print("-" * 125)

    # 1. 최고 기록 및 지배력 체크
    metrics = ["hp", "mp", "sp", "dmg"]
    audit_passed = True

    for m in metrics:
        top = max(matrix_results, key=lambda x: x[m] if x["lv"] == 50 else 0)
        print(f" [BEST IN {m.upper():<3}] {top['key'].upper():<25} -> {top[m]}")
        dominance_tracker[top['key']] += 1

    print("-" * 125)
    
    # 지배력 경고 (Elf Mage All-in-one 방지)
    for comb, score in dominance_tracker.items():
        if score > MAX_DOMINANCE_SCORE:
            print(f" ❌ FAILURE: {comb.upper()} is too dominant (Score: {score}). Meta breakdown risk!")
            audit_passed = False

    # 2. 직업 간 AP 격차 체크 (Warrior vs Rogue) - Sepration Audit
    warrior_ap_50 = [x["ap"] for x in matrix_results if x["class"] == "warrior" and x["lv"] == 50]
    rogue_ap_50 = [x["ap"] for x in matrix_results if x["class"] == "rogue" and x["lv"] == 50]
    avg_war_ap = sum(warrior_ap_50) / len(warrior_ap_50)
    avg_rog_ap = sum(rogue_ap_50) / len(rogue_ap_50)
    ap_gap = ((avg_war_ap / avg_rog_ap) - 1) * 100

    print(f" [AP GAP CHECK] Warrior vs Rogue Separation: {ap_gap:.1f}% higher for Warrior.")
    if ap_gap < MIN_CLASS_AP_GAP_PERCENT:
        print(f" ❌ FAILURE: Melee AP separation is insufficient (<{MIN_CLASS_AP_GAP_PERCENT}%).")
        audit_passed = False

    # 3. 인간(Human)의 정체성 체크 (Versatility Audit)
    human_sp = [x["sp"] for x in matrix_results if x["race"] == "human" and x["lv"] == 50]
    all_avg_sp = sum(x["sp"] for x in matrix_results if x["lv"] == 50) / len([x for x in matrix_results if x["lv"] == 50])
    human_sp_ratio = (sum(human_sp)/len(human_sp)) / all_avg_sp
    print(f" [HUMAN VERSATILITY] Human SP vs Global Average: {human_sp_ratio*100:.1f}%.")
    # 인간은 '무난함'을 넘어 하이브리드 잠재력이 있어야 함.

    # 4. TTK 및 레벨별 성장 안정성
    ttk_values = [x["ttk"] for x in matrix_results if x["lv"] == 50]
    avg_ttk = sum(ttk_values) / len(ttk_values)
    print(f" [TTK STABILITY] Global Avg TTK: {avg_ttk:.1f} turns. (Target: {TARGET_TTK_MIN}~{TARGET_TTK_MAX})")

    print("-" * 125)
    if audit_passed:
        print(f"{'✅ AUDIT PASSED: Current numbers are within safe design limits.':^125}")
    else:
        print(f"{'⚠️ AUDIT FAILED: Balance adjustments required in JSON data files.':^125}")
    print("=" * 125)

if __name__ == "__main__":
    run_full_matrix_simulation()