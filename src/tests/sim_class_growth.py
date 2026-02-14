# File: src/tests/sim_class_growth.py
import sys
import os
import math

# 프로젝트 루트를 자동으로 찾아 sys.path에 추가
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../"))
cwd = os.getcwd()

for path in [project_root, cwd]:
    if path not in sys.path and os.path.exists(os.path.join(path, "src")):
        sys.path.insert(0, path)

from src.core.factory import EntityFactory
from src.systems.growth_system import GrowthSystem

def run_tdd_simulation():
    print("=" * 70)
    print("🧪 [TDD Simulation] Race & Class Synergy Matrix")
    print("=" * 70)
    
    # 테스트할 종족과 직업 조합 (대표적인 시너지/역시너지 조합)
    test_matrix = [
        ("orc", "warrior"),    # 시너지: 극강의 탱커
        ("elf", "mage"),       # 시너지: 극강의 마법사
        ("human", "rogue"),    # 밸런스: 표준 도적
        ("dwarf", "warrior"),  # 시너지: 단단한 전사
        ("orc", "mage")        # 역시너지: 지능 낮은 마법사 (성능 확인용)
    ]
    
    results = []

    for race_id, cls_id in test_matrix:
        print(f"\n▶ Testing Combination: {race_id.upper()} {cls_id.upper()}")
        print("-" * 45)
        
        try:
            player = EntityFactory.create_player(f"{race_id}_{cls_id}", race_id, cls_id)
        except Exception as e:
            print(f"❌ 생성 실패: {race_id}/{cls_id} - {e}")
            import traceback
            traceback.print_exc()
            continue
            
        # Lv.1 초기 상태 기록
        init_hp = player.max_hp
        init_mp = player.max_mp
        
        # Lv.50 만레벨 시뮬레이션 (성장 곡선의 끝단 확인)
        player.level = 50
        GrowthSystem.refresh_stats(player)
        
        final_hp = player.max_hp
        final_mp = player.max_mp
        final_str = GrowthSystem.get_scaled_stat(player, "strength")
        final_int = GrowthSystem.get_scaled_stat(player, "intelligence")
        
        print(f" [Lv.1  -> Lv.50] Result")
        print(f"  - HP: {init_hp} -> {final_hp} (Growth: x{final_hp/init_hp:.2f})")
        print(f"  - MP: {init_mp} -> {final_mp} (Growth: x{final_mp/init_mp:.2f})")
        print(f"  - Main Stat (STR/INT): {final_str} / {final_int}")
        
        # 조합별 논리 검증
        if race_id == "orc" and cls_id == "warrior":
            if final_hp > 3500:
                print(" ✅ PASS: Orc Warrior HP is legendary.")
            else:
                print(" ❌ FAIL: Orc Warrior HP lower than expected.")
                
        if race_id == "elf" and cls_id == "mage":
            if final_mp > 2000:
                print(" ✅ PASS: Elf Mage Mana is overwhelming.")
            else:
                print(" ❌ FAIL: Elf Mage Mana lower than expected.")

        if race_id == "orc" and cls_id == "mage":
            # 오크 마법사는 엘프 마법사보다 마나가 현저히 적어야 함
            if final_mp < 2000: # 조정된 기준 (오크 법사도 성장은 하므로)
                print(" ✅ PASS: Orc Mage Mana is appropriately penalized by base stats.")
            else:
                print(" ❌ FAIL: Orc Mage Mana is too high for their low intelligence.")

    print("\n" + "=" * 70)
    print("🏆 SIMULATION COMPLETE: Race/Class Matrix Analysis Finished.")
    print("=" * 70)

if __name__ == "__main__":
    run_tdd_simulation()