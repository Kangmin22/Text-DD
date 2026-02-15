import time
import random
from src.core.state_machine import State
from src.core.factory import EntityFactory
from src.core.context import GameContext
from src.utils.data_loader import DataLoader
from src.states.combat_state import CombatState

class DungeonState(State):
    def __init__(self, floor=1):
        self.floor = floor
        self.steps = 0
        self.monster_pool = []
        self._load_monsters()

    def _load_monsters(self):
        all_monsters = DataLoader.load_json("monsters.json")
        if not all_monsters:
            self.monster_pool = []
            return

        max_cr = max(1, self.floor * 1.5)
        valid_mobs = []
        for mid, data in all_monsters.items():
            lvl = data.get("level", 0)
            if lvl <= max_cr:
                valid_mobs.append(mid)
        
        self.monster_pool = valid_mobs if valid_mobs else list(all_monsters.keys())

    def update(self):
        player = GameContext.get_player()
        if player.current_hp <= 0:
            print("\n💀 당신은 던전에서 쓰러졌습니다...")
            input(" (엔터키를 눌러 마을로 귀환) ")
            player.current_hp = 1
            from src.states.town_state import TownState
            self.manager.change(TownState())
            return

        print("\n" + "="*50)
        print(f" 💀 [ 깊은 숲 - 지하 {self.floor}층 ]")
        print(f" 👣 진행도: {self.steps}/10  |  ❤️ HP: {player.current_hp}")
        print("="*50)
        print(" 1. 🔦 앞으로 나아간다 (탐험)")
        print(" 2. ⛺ 잠시 휴식 (Risk: 기습)")
        print(" 3. 🏃 마을로 도망친다")
        print("-"*50)

    def handle_input(self, user_input: str):
        if user_input == '1':
            self._explore()
        elif user_input == '2':
            self._rest()
        elif user_input == '3':
            print("\n💨 허겁지겁 숲을 빠져나갑니다!")
            from src.states.town_state import TownState
            self.manager.change(TownState())

    def _explore(self):
        self.steps += 1
        print("\n👣 뚜벅... 뚜벅...")
        time.sleep(0.5)

        if self.steps >= 10:
            print("\n✨ 아래층으로 내려가는 계단을 발견했습니다!")
            sel = input(" [1: 내려간다] [2: 머무른다] >> ")
            if sel == '1':
                self.manager.change(DungeonState(self.floor + 1))
            return

        roll = random.randint(1, 100)
        if roll <= 50: 
            self._trigger_combat()
        elif roll <= 70:
            msg = random.choice(["바람 소리가 들립니다.", "멀리서 늑대 울음소리가...", "길이 조용합니다."])
            print(f" ...{msg}")
        elif roll <= 85: 
            player = GameContext.get_player()
            heal = int(player.max_hp * 0.1)
            player.current_hp = min(player.max_hp, player.current_hp + heal)
            print(f" 🍓 산딸기를 발견했습니다! 체력이 {heal} 회복됩니다.")
        else: 
            player = GameContext.get_player()
            dmg = int(player.max_hp * 0.05)
            player.current_hp -= dmg
            print(f" 💢 가시덤불에 긁혔습니다! {dmg} 피해.")

    def _trigger_combat(self):
        if not self.monster_pool:
            print(" (몬스터가 없는 층입니다)")
            return

        mid = random.choice(self.monster_pool)
        monster = EntityFactory.create_monster(mid)
        
        if monster:
            print(f"\n🔥 야생의 [{monster.name}] (Lv.{monster.level}) 등장!")
            time.sleep(1)
            self.manager.push(CombatState(enemies=[monster]))

    def _rest(self):
        player = GameContext.get_player()
        print("\n⛺ 쪽잠을 잡니다...")
        time.sleep(1)
        if random.random() < 0.3:
            print(" ⚡ 으악! 자는 도중 몬스터가 습격했습니다!")
            self._trigger_combat()
        else:
            heal = int(player.max_hp * 0.2)
            player.current_hp = min(player.max_hp, player.current_hp + heal)
            print(f" ✨ 개운합니다. 체력이 {heal} 회복되었습니다.")