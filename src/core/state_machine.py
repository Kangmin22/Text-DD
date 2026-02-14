import os
from abc import ABC, abstractmethod

class State(ABC):
    def __init__(self):
        self.manager = None

    def on_enter(self, machine): pass
    def on_exit(self, machine): pass
    def update(self): pass
    def handle_input(self, user_input): pass

class StateMachine:
    def __init__(self, initial_state, game_data=None):
        self.stack = []
        self.game_data = game_data or {}
        if initial_state:
            self.push(initial_state)

    def push(self, state):
        if self.stack:
            self.stack[-1].on_exit(self)
        
        self.stack.append(state)
        state.manager = self # 상태가 매니저(머신)에 접근할 수 있게 함
        state.on_enter(self)

    def pop(self):
        if len(self.stack) > 0:
            exiting_state = self.stack.pop()
            exiting_state.on_exit(self)
            
        if self.stack:
            self.stack[-1].on_enter(self)

    def change(self, state):
        """현재 상태를 제거하고 새로운 상태로 교체합니다."""
        if len(self.stack) > 0:
            exiting_state = self.stack.pop()
            exiting_state.on_exit(self)
            
        self.stack.append(state)
        state.manager = self
        state.on_enter(self)

    def update(self):
        if self.stack:
            self.stack[-1].update()

    def handle_input(self, user_input):
        if self.stack:
            self.stack[-1].handle_input(user_input)