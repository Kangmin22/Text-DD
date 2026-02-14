# File: src/main.py
import sys
import os
import time

# --- 경로 설정 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.engine import GameEngine
from src.core.state_machine import State
from src.core.factory import EntityFactory
from src.systems.growth_system import GrowthSystem
from src.systems.combat_system import CombatSystem
from src.systems.inventory_system import InventorySystem
from src.models.combat_context import CombatContext

# --- 전역 변수 (간이 세션 저장용) ---
session_player = None

class TitleState(State):
    def update(self):
        print("\n" + "="*45)
        print("   DND TEXT RPG: THE MECHANICS v9.0")
        print("="*45)
        print(" 1. 새 게임 시작 (테스트 캐릭터)")
        print(" Q. 게임 종료")
        print("="*45)

    def handle_input(self, user_input: str):
        global session_player
        if user_input == '1':
            print("\n>> 주사위를 굴려 운명을 결정하는 중...")
            try:
                # 20레벨 Orc Warrior 생성 (전투 테스트용)
                player = EntityFactory.create_player("Player", "orc", "warrior")
                player.level = 20
                GrowthSystem.refresh_stats(player)
                
                session_player = player
                print(f"✅ 캐릭터 생성 성공!")
                print(f"   이름: {player.name} | 종족: {player.race_id.upper()} | 직업: {player.class_id.upper()}")
                
                self.manager.change(TownState())
            except Exception as e:
                print(f"❌ 생성 실패: {e}")
                import traceback
                traceback.print_exc()
        elif user_input.lower() == 'q':
            sys.exit()

class TownState(State):
    def update(self):
        global session_player
        hp_ratio = int((session_player.current_hp / session_player.max_hp) * 100)
        
        print("\n" + "-"*45)
        print(f" [ 마 을 ] 현재 상태: {session_player.name}")
        print(f" 체력: {session_player.current_hp}/{session_player.max_hp} [{hp_ratio}%]")
        print("-"*45)
        print(" 1. 전투 훈련장 (Combat Test)")
        print(" 2. 타이틀로 돌아가기")
        print(" 3. [TEST] 보급품 받기 & 장착 테스트")
        print(" 4. 여관에서 휴식 (HP 완전 회복)")
        print("-"*45)

    def handle_input(self, user_input: str):
        global session_player
        if user_input == '1':
            self.manager.push(CombatState())
        elif user_input == '2':
            self.manager.change(TitleState())
        elif user_input == '3':
            self._run_inventory_test()
        elif user_input == '4':
            print("\n💤 여관에서 푹 쉬었습니다. 체력이 완전히 회복되었습니다!")
            session_player.current_hp = session_player.max_hp
            
    def _print_stats(self, actor, label: str):
        str_val = GrowthSystem.get_scaled_stat(actor, "strength")
        dex_val = GrowthSystem.get_scaled_stat(actor, "dexterity")
        con_val = GrowthSystem.get_scaled_stat(actor, "constitution")
        
        print(f" 📊 [{label}]")
        print(f"   HP: {actor.max_hp} | STR: {str_val} | DEX: {dex_val} | CON: {con_val}")

    def _run_inventory_test(self):
        global session_player
        print("\n📦 [보급품 도착] 상자를 열어보니 찬란한 빛이 뿜어져 나옵니다!")
        
        items = [
            EntityFactory.create_item("rusty_greatsword"),
            EntityFactory.create_item("leather_armor"),
            EntityFactory.create_item("ring_of_vitality")
        ]
        
        for item in items:
            if item:
                stats_info = ", ".join([f"{k.upper()} +{v}" for k, v in item.bonus_stats.items()])
                print(f"   - 🎁 발견: [{item.name}] | {stats_info}")
                InventorySystem.add_item(session_player, item)
        
        print("-" * 45)
        self._print_stats(session_player, "장착 전 능력치")
        
        print("\n🛠️ [자동 장착] 장비를 착용하여 전의를 다집니다...")
        for item in items:
            if item:
                InventorySystem.equip_item(session_player, item)
        
        session_player.current_hp = session_player.max_hp
        print("   (보너스: 장비 착용의 활력으로 HP가 모두 회복되었습니다!)")
        
        print("-" * 45)
        self._print_stats(session_player, "장착 후 능력치")

class CombatState(State):
    def on_enter(self, prev_state=None):
        global session_player
        print("\n" + "!"*45)
        print("        전 투 가  시 작 되 었 습 니 다 ! ")
        print("!"*45)
        
        enemy = EntityFactory.create_player("Training Dummy", "human", "guardian")
        enemy.level = 20
        GrowthSystem.refresh_stats(enemy)
        
        self.ctx = CombatContext(player=session_player, enemy=enemy)

    def _draw_hp_bar(self, current, max_hp, length=20):
        ratio = max(0, min(1, current / max_hp))
        filled = int(length * ratio)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {current}/{max_hp}"

    def update(self):
        if self.ctx.is_finished:
            print(f"\n🏆 최종 승자: {self.ctx.winner.name}!")
            print("   (아무 키나 누르면 마을로 돌아갑니다.)")
            return

        p = self.ctx.player
        e = self.ctx.enemy
        
        print("\n" + "━"*45)
        print(f" [TURN {self.ctx.turn_count}]")
        print(f" {p.name:<15} {self._draw_hp_bar(p.current_hp, p.max_hp)}")
        print(f" {e.name:<15} {self._draw_hp_bar(e.current_hp, e.max_hp)}")
        print("━"*45)
        print(" >> [Enter] 공격 진행 | [run] 도망치기")

    def handle_input(self, user_input: str):
        if self.ctx.is_finished:
            self.manager.pop()
            return

        if user_input.lower() == 'run':
            print("\n💨 비겁하지만 현명합니다! 전장을 이탈했습니다.")
            self.manager.pop()
            return

        # 턴 처리 및 로그 출력
        CombatSystem.process_turn(self.ctx)
        
        print("\n" + " . "*15)
        for log in self.ctx.logs:
            print(f" {log}")
            time.sleep(0.1) # 로그 읽는 맛을 위해 아주 살짝 딜레이
        self.ctx.logs.clear()

if __name__ == "__main__":
    app = GameEngine()
    app.state_machine.change(TitleState())
    app.run()