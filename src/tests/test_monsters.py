import sys
import os

# 프로젝트 루트 경로 추가
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
sys.path.insert(0, PROJECT_ROOT)

from src.core.factory import EntityFactory
from src.systems.growth_system import GrowthSystem

def run_monster_test():
    print("=" * 80)
    print(f"{'D&D Monster Spawn Test (Roguelike Balanced)':^80}")
    print("=" * 80)

    # 테스트할 몬스터 ID 목록
    target_monsters = [
        "crab",             # CR 0
        "ape",              # CR 1/2
        "worg",             # CR 1/2
        "brown_bear",       # CR 1
        "mammoth"           # CR 6
    ]

    print(f"{'Name':<25} | {'Lv':<4} | {'HP':<6} | {'ATK':<4} | {'DEX':<4} | {'Eva(%)':<6}")
    print("-" * 80)

    for mid in target_monsters:
        monster = EntityFactory.create_monster(mid)
        
        if not monster:
            print(f"❌ {mid} 소환 실패")
            continue
            
        # 스탯 확인
        hp = monster.max_hp
        atk = GrowthSystem.get_attack_power(monster)
        dex = GrowthSystem.get_scaled_stat(monster, "dexterity")
        eva = GrowthSystem.get_evasion(monster) * 100
        
        print(f"{monster.name:<25} | {monster.level:<4} | {hp:<6} | {atk:<4} | {dex:<4} | {eva:.1f}%")

    print("-" * 80)
    print("💡 밸런스 점검 포인트:")
    print(" 1. HP가 수천 단위에서 수백 단위로 줄었는지 확인 (긴장감 조성)")
    print(" 2. ATK 수치와 HP 비율이 약 1:5 ~ 1:8 정도인지 확인 (4~8턴 킬각)")
    print(" 3. 고양이(Cat/Crab)가 탱크가 아닌 '약한 생명체'로 돌아왔는지 확인")
    print("=" * 80)

if __name__ == "__main__":
    run_monster_test()