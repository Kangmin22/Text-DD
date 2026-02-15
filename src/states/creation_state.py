import time
from src.core.state_machine import State
from src.core.factory import EntityFactory
from src.core.context import GameContext
from src.systems.growth_system import GrowthSystem
from src.systems.inventory_system import InventorySystem
from src.utils.data_loader import DataLoader

class CharacterCreationState(State):
    def __init__(self):
        self.step = 0  # 0:이름, 1:종족, 2:직업, 3:확인
        self.char_data = {"name": "", "race": "", "class": ""}
        
        self.races = DataLoader.load_json("races.json")
        self.classes = DataLoader.load_json("classes.json")
        
        self.race_list = sorted(list(self.races.keys())) if self.races else []
        self.class_list = sorted(list(self.classes.keys())) if self.classes else []

    def update(self):
        print("\n" + "="*50)
        print(f"{'📝 캐릭터 생성':^50}")
        print("="*50)
        
        if self.step == 0:
            print(" 당신의 이름을 알려주세요.")
            print(" (입력 후 엔터)")
            print("-" * 50)
            
        elif self.step == 1:
            print(f" [ 종족 선택 ] - {self.char_data['name']}님, 당신의 출신은?")
            print("-" * 50)
            if not self.race_list:
                print(" (종족 데이터가 없습니다. races.json을 확인하세요)")
                return
                
            for idx, r_id in enumerate(self.race_list):
                r_data = self.races[r_id]
                bonuses = []
                for stat, val in r_data.get("base_stats", {}).items():
                    if val > 0: bonuses.append(f"{stat[:3].upper()}+{val}")
                bonus_str = " ".join(bonuses)
                
                print(f" {idx+1}. {r_data.get('name', r_id)} | {bonus_str}")
            print("-" * 50)
            print(" 번호를 선택하세요 >> ", end="")
            
        elif self.step == 2:
            print(f" [ 직업 선택 ] - {self.char_data['race'].upper()} 종족이시군요.")
            print("-" * 50)
            if not self.class_list:
                print(" (직업 데이터가 없습니다. classes.json을 확인하세요)")
                return
                
            for idx, c_id in enumerate(self.class_list):
                c_data = self.classes[c_id]
                hd = c_data.get("hit_dice", "?")
                skills = ", ".join(c_data.get("initial_skills", []))
                print(f" {idx+1}. {c_data.get('name', c_id)} (HD: {hd}) | 스킬: {skills}")
            print("-" * 50)
            print(" 번호를 선택하세요 >> ", end="")
            
        elif self.step == 3:
            print(" [ 최종 확인 ]")
            print("-" * 50)
            print(f" 이름: {self.char_data['name']}")
            print(f" 종족: {self.char_data['race'].upper()}")
            print(f" 직업: {self.char_data['class'].upper()}")
            print("-" * 50)
            print(" 이대로 시작하시겠습니까? (Y/N) >> ", end="")

    def handle_input(self, user_input: str):
        if not user_input.strip(): return

        if self.step == 0:
            self.char_data["name"] = user_input.strip()
            self.step += 1
            
        elif self.step == 1:
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(self.race_list):
                    self.char_data["race"] = self.race_list[idx]
                    self.step += 1
                else:
                    print("❌ 올바른 번호를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")

        elif self.step == 2:
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(self.class_list):
                    self.char_data["class"] = self.class_list[idx]
                    self.step += 1
                else:
                    print("❌ 올바른 번호를 입력해주세요.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")

        elif self.step == 3:
            if user_input.lower() == 'y':
                self._create_character()
            elif user_input.lower() == 'n':
                print("처음부터 다시 선택합니다.")
                self.step = 0
            else:
                print("Y 또는 N을 입력해주세요.")

    def _create_character(self):
        print("\n>> ✨ 영혼을 불어넣는 중...")
        try:
            name = self.char_data['name']
            race = self.char_data['race']
            job = self.char_data['class']
            
            player = EntityFactory.create_player(name, race, job)
            player.level = 1
            
            weapon = EntityFactory.create_item("rusty_greatsword")
            if weapon: InventorySystem.equip_item(player, weapon)

            if not player.skills:
                player.skills = ["basic_attack", "power_strike"]
            if "basic_attack" not in player.skills:
                player.skills.insert(0, "basic_attack")

            GrowthSystem.refresh_stats(player)
            
            # [중요] 전역 컨텍스트에 플레이어 저장
            GameContext.set_player(player)
            
            print("✅ 캐릭터 생성 완료!")
            time.sleep(1)
            
            from src.states.town_state import TownState
            self.manager.change(TownState())
            
        except Exception as e:
            print(f"❌ 캐릭터 생성 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
            from src.states.title_state import TitleState
            self.manager.change(TitleState())