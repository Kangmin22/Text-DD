import sys
from src.core.state_machine import State
# 순환 참조 방지를 위해 메서드 내부에서 import 할 수도 있지만, 
# 여기서는 다음 상태인 CreationState를 import 해야 합니다.
# (파일이 분리되었으므로 생성 시점에 import 하는 방식을 사용합니다)

class TitleState(State):
    def update(self):
        print("\n" + "="*50)
        print(f"{'⚔️  DND TEXT RPG: THE ABYSS WALKER  ⚔️':^50}")
        print("="*50)
        print(" 1. 새로운 모험 시작 (New Game)")
        print(" Q. 종료 (Quit)")
        print("="*50)

    def handle_input(self, user_input: str):
        if user_input == '1':
            # 파일이 분리되었으므로 필요한 시점에 import
            from src.states.creation_state import CharacterCreationState
            self.manager.change(CharacterCreationState())
        elif user_input.lower() == 'q':
            print("👋 모험을 종료합니다.")
            sys.exit()