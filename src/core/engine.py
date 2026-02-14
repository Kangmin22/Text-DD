import sys
from .state_machine import StateMachine, State

class EmptyState(State):
    def on_enter(self, machine): pass
    def update(self, machine): pass
    def handle_input(self, machine, user_input): pass

class GameEngine:
    def __init__(self):
        # Start with an empty state to avoid dependency issues (like missing player for CombatState)
        initial_state = EmptyState()
        self.state_machine = StateMachine(initial_state, game_data={"player": None})
        self.running = True

    def run(self):
        while self.running:
            try:
                self.state_machine.update()
                
                # Basic input handling loop
                user_input = input(">> ")
                if user_input.lower() == 'quit':
                    self.running = False
                    break
                    
                self.state_machine.handle_input(user_input)
                
            except KeyboardInterrupt:
                self.running = False
                sys.exit()
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                self.running = False