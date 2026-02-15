import time
from src.core.state_machine import State
from src.core.context import GameContext
from src.core.factory import EntityFactory
from src.systems.growth_system import GrowthSystem
from src.states.combat_state import CombatState
from src.states.dungeon_state import DungeonState

class TownState(State):
    def update(self):
        player = GameContext.get_player()
        # 플레이어가 없으면 타이틀로 강제 이동 (안전장치)
        if not player:
            from src.states.title_state import TitleState
            self.manager.change(TitleState())
            return

        hp_per = int((player.current_hp / player.max_hp) * 100)
        
        print("\n" + "-"*50)
        print(f" 🏰 [ 안전한 마을 ] - {player.name} ({player.race_id.title()} {player.class_id.title()})")
        print(f" ❤️  HP: {player.current_hp}/{player.max_hp} ({hp_per}%)")
        print(f" 💧 MP: {player.current_mp}/{player.max_mp}")
        print("-" * 50)
        
        s = player
        str_v = GrowthSystem.get_scaled_stat(s, "strength")
        dex_v = GrowthSystem.get_scaled_stat(s, "dexterity")
        int_v = GrowthSystem.get_scaled_stat(s, "intelligence")
        print(f" [스탯] STR:{str_v} DEX:{dex_v} INT:{int_v} ...")
        print("-" * 50)
        print(" 1. 🌲 어둠의 숲 탐험 (Dungeon Start)")
        print(" 2. ⚔️ 전투 훈련장 (Dummy Test)")
        print(" 3. 📦 인벤토리 & 장비 확인")
        print(" 4. 💤 여관에서 휴식 (HP/MP 회복)")
        print(" 5. 🔙 타이틀로")
        print("-"*50)

    def handle_input(self, user_input: str):
        player = GameContext.get_player()
        
        if user_input == '1':
            self.manager.change(DungeonState(floor=1))
        elif user_input == '2':
            dummy = EntityFactory.create_player("Training Dummy", "human", "warrior")
            dummy.level = player.level
            GrowthSystem.refresh_stats(dummy)
            self.manager.push(CombatState(enemies=[dummy]))
        elif user_input == '3':
            self._show_inventory()
        elif user_input == '4':
            print("\n💤 따뜻한 침대에서 푹 쉽니다... (HP/MP 완전 회복)")
            player.current_hp = player.max_hp
            player.current_mp = player.max_mp
            time.sleep(1)
        elif user_input == '5':
            from src.states.title_state import TitleState
            self.manager.change(TitleState())

    def _show_inventory(self):
        player = GameContext.get_player()
        print("\n" + "="*30)
        print(" [ 장비 현황 ]")
        eq = player.equipment
        print(f" 🗡️  무기: {eq['main_hand'].name if eq['main_hand'] else '(없음)'}")
        print(f" 🛡️  갑옷: {eq['body'].name if eq['body'] else '(없음)'}")
        print(f" 💍  반지: {eq['ring'].name if eq['ring'] else '(없음)'}")
        
        atk = GrowthSystem.get_attack_power(player)
        defense = int(GrowthSystem.get_defense(player) * 100)
        evasion = int(GrowthSystem.get_evasion(player) * 100)
        print("-" * 30)
        print(f" 💪 공격력: {atk}")
        print(f" 🛡️ 피해감소: {defense}%")
        print(f" 💨 회피율: {evasion}%")
        print("="*30)
        input(" (엔터를 누르면 돌아갑니다) ")