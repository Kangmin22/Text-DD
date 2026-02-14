# File: src/models/combat_context.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from src.models.actor import Actor

@dataclass
class CombatContext:
    """
    전투의 실시간 상태를 저장하는 순수 데이터 모델.
    시스템이 이 데이터를 참조하여 전투를 진행함.
    """
    participants: List[Actor] = field(default_factory=list)
    enemies: List[Actor] = field(default_factory=list)
    
    # 주도권(Initiative) 순서대로 정렬된 액터 ID 리스트
    turn_order: List[str] = field(default_factory=list)
    current_turn_index: int = 0
    round_count: int = 1
    
    is_finished: bool = False
    winner_side: Optional[str] = None # "player" or "enemy"
    
    # 전투 중 발생한 이벤트 로그 (최근 5~10개 표시용)
    combat_logs: List[str] = field(default_factory=list)

    def add_log(self, message: str):
        self.combat_logs.append(message)
        if len(self.combat_logs) > 10:
            self.combat_logs.pop(0)

    @property
    def current_actor(self) -> Optional[Actor]:
        if not self.turn_order:
            return None
        current_id = self.turn_order[self.current_turn_index]
        for p in self.participants + self.enemies:
            if p.id == current_id:
                return p
        return None