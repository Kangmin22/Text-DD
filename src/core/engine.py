# src/core/engine.py
import sys
from .state_machine import StateMachine

class GameEngine:
    def __init__(self):
        self.state_machine = StateMachine()
        self.is_running = True

    def run(self):
        print("=== DND TEXT RPG ENGINE STARTED ===")
        print("명령어 힌트: 'quit' to exit")
        
        while self.is_running:
            # 1. 현재 상태 정보 출력 (UI 대용)
            current_state = self.state_machine.get_current_state_name()
            print(f"\n[Current State: {current_state}]")
            
            # 2. Update (로직 처리)
            self.state_machine.update()
            
            # 3. Input Handling (입력 대기)
            # 실제 TUI에서는 비동기 입력이지만, 지금은 input() 블로킹 사용
            try:
                user_input = input(">> ").strip().lower()
            except KeyboardInterrupt:
                print("\nForce Quitting...")
                break

            if user_input == 'quit' and current_state == 'TitleState':
                self.is_running = False
                print("Engine Shutdown.")
                break
            
            # 상태 머신으로 입력 전달
            self.state_machine.handle_input(user_input)