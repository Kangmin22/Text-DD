# File: src/models/combat_context.py
from dataclasses import dataclass, field
from typing import List, Optional
from src.models.actor import Actor

@dataclass
class CombatContext:
    """
    단일 전투 세션의 상태를 저장하는 컨텍스트 모델.
    전투 중 발생하는 로그와 턴 정보, 승패 여부를 관리합니다.
    """
    player: Actor
    enemy: Actor
    turn_count: int = 0
    is_finished: bool = False
    winner: Optional[Actor] = None
    
    # [Critical] 로그를 저장할 리스트 필드 (이게 없어서 오류가 났습니다!)
    logs: List[str] = field(default_factory=list)

    def get_current_attacker(self) -> Actor:
        # 단순 턴제: 짝수 턴은 플레이어, 홀수 턴은 적
        return self.player if self.turn_count % 2 == 0 else self.enemy

    def get_current_defender(self) -> Actor:
        return self.enemy if self.turn_count % 2 == 0 else self.player