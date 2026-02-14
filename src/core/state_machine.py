# src/core/state_machine.py
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional

class State(ABC):
    """
    모든 게임 상태(Scene)의 부모 클래스.
    이 인터페이스를 상속받아 TitleState, TownState 등을 구현한다.
    """
    def __init__(self):
        self.manager = None # StateMachine 참조
        self.context = {}   # 직렬화 대상이 되는 상태 내부 데이터

    def on_enter(self, prev_state=None):
        """상태가 스택에 들어올 때 (초기화)"""
        pass

    def on_exit(self):
        """상태가 스택에서 나갈 때 (정리)"""
        pass

    def on_resume(self):
        """상위 상태가 pop되어 다시 활성화될 때"""
        pass

    @abstractmethod
    def update(self):
        """매 프레임 로직 처리"""
        pass

    @abstractmethod
    def handle_input(self, user_input: str):
        """사용자 입력 처리"""
        pass

class StateMachine:
    """
    State 객체들을 스택(Stack)으로 관리하는 매니저.
    """
    def __init__(self):
        self.stack: List[State] = []

    def push(self, state: State):
        """현재 상태를 유지한 채, 새로운 상태를 위에 쌓음 (예: 인벤토리 열기)"""
        if self.stack:
            # 기존 상태는 멈춤(Pause) 느낌
            pass
        
        state.manager = self
        self.stack.append(state)
        print(f"[FSM] Push: {state.__class__.__name__} (Stack Size: {len(self.stack)})")
        state.on_enter()

    def pop(self):
        """현재 상태를 종료하고 이전 상태로 돌아감 (예: 인벤토리 닫기)"""
        if not self.stack:
            return
        
        removed_state = self.stack.pop()
        print(f"[FSM] Pop: {removed_state.__class__.__name__}")
        removed_state.on_exit()

        if self.stack:
            current = self.stack[-1]
            print(f"[FSM] Resume: {current.__class__.__name__}")
            current.on_resume()

    def change(self, state: State):
        """스택을 모두 비우고(혹은 현재 상태 교체) 새로운 상태로 전환 (예: 타이틀 -> 마을)"""
        while self.stack:
            removed = self.stack.pop()
            removed.on_exit()
        
        state.manager = self
        self.stack.append(state)
        print(f"[FSM] Change: {state.__class__.__name__}")
        state.on_enter()

    def update(self):
        """현재 활성화된(스택 최상단) 상태의 update 실행"""
        if self.stack:
            self.stack[-1].update()

    def handle_input(self, user_input: str):
        """현재 활성화된 상태에게 입력 전달"""
        if self.stack:
            self.stack[-1].handle_input(user_input)
    
    def get_current_state_name(self) -> str:
        return self.stack[-1].__class__.__name__ if self.stack else "None"