import sys
import os
import random
import time

# 프로젝트 루트 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
sys.path.insert(0, PROJECT_ROOT)

from src.core.factory import EntityFactory
from src.utils.data_loader import DataLoader
from src.systems.growth_system import GrowthSystem
from src.systems.combat_system import CombatSystem
from src.models.combat_context import CombatContext

def run_random_encounter():
    print("=" * 60)
    print(f"{'⚔️  ROGUELIKE RANDOM ENCOUNTER TEST  ⚔️':^60}")
    print("=" * 60)

    # 1. 몬스터 목록 로드
    monster_data = DataLoader.load_json("monsters.json")
    if not monster_data:
        print("❌ 몬스터 데이터(monsters.json)가 비어있습니다!")
        return

    monster_ids = list(monster_data.keys())
    print(f"🔥 [던전 입장] 어둠 속에서 {len(monster_ids)}종의 기척이 느껴집니다...")
    
    # 2. 랜덤 몬스터 출현!
    random_mid = random.choice(monster_ids)
    monster = EntityFactory.create_monster(random_mid)
    
    if not monster:
        print(f"❌ 몬스터 생성 실패: {random_mid}")
        return

    print(f"\n⚠️  야생의 [{monster.name}] (Lv.{monster.level}) 이(가) 나타났다!")
    print(f"    HP: {monster.max_hp} | STR: {GrowthSystem.get_scaled_stat(monster, 'strength')} | DEX: {GrowthSystem.get_scaled_stat(monster, 'dexterity')}")

    # 3. 플레이어 준비
    player = EntityFactory.create_player("Adventurer", "human", "fighter")
    print(f"\n🛡️  [{player.name}] (Lv.{player.level} Human Fighter) 전투 준비 완료!")
    print(f"    HP: {player.max_hp} | STR: {GrowthSystem.get_scaled_stat(player, 'strength')}")

    # 4. 약식 전투 시뮬레이션
    print("-" * 60)
    print("전투 시작! (3초 후 결과 공개)")
    time.sleep(1)
    print("Checking stats...", end="\r")
    
    # 간단한 승률 예측 (CombatSystem을 풀로 돌리기엔 코드가 길어지므로 스탯 비교)
    p_power = GrowthSystem.get_attack_power(player)
    m_power = GrowthSystem.get_attack_power(monster)
    
    print(f"⚔️  전투력 비교 - 플레이어: {p_power} vs 몬스터: {m_power}      ")
    time.sleep(1)

    # 실제 전투 로직 살짝 맛보기
    ctx = CombatContext(player, [monster])
    
    turn = 1
    while not ctx.is_finished and turn <= 10:
        # 플레이어 턴
        dmg = max(1, p_power - GrowthSystem.get_scaled_stat(monster, 'constitution'))
        monster.current_hp -= dmg
        print(f" [Turn {turn}] 플레이어가 {monster.name}에게 {dmg} 피해! (남은 HP: {max(0, monster.current_hp)})")
        
        if monster.current_hp <= 0:
            print(f"\n🎉 승리! {monster.name}을(를) 처치했습니다!")
            break
            
        # 몬스터 턴
        dmg_m = max(1, m_power - GrowthSystem.get_scaled_stat(player, 'constitution'))
        player.current_hp -= dmg_m
        print(f" [Turn {turn}] {monster.name}이(가) 플레이어에게 {dmg_m} 피해! (남은 HP: {max(0, player.current_hp)})")
        
        if player.current_hp <= 0:
            print(f"\n💀 패배... {monster.name}에게 당했습니다.")
            break
            
        turn += 1
        time.sleep(0.5)
    
    if turn > 10:
        print("\n💨 무승부! 서로 지쳐서 물러납니다.")

    print("=" * 60)

if __name__ == "__main__":
    run_random_encounter()