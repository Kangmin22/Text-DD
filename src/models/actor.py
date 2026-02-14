# File: src/models/actor.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional
# 순환 참조 방지를 위해 TYPE_CHECKING을 쓸 수도 있지만, 
# 간단한 구조이므로 여기서는 문자열로 타입 힌트 처리를 하거나 Item을 임포트하지 않고 처리합니다.

@dataclass
class Actor:
    """
    게임 내 등장하는 모든 캐릭터(플레이어, 몬스터)의 기본 데이터 모델.
    """
    id: str
    name: str
    race_id: str
    class_id: str
    
    level: int = 1
    
    current_hp: int = 0
    max_hp: int = 0 
    
    # 스탯 및 특성
    base_stats: Dict[str, int] = field(default_factory=dict)
    keystones: Dict[str, bool] = field(default_factory=dict)

    # [New] 인벤토리 및 장비
    # inventory: 소지품 리스트 (Item 객체들이 들어감)
    inventory: List = field(default_factory=list)
    
    # equipment: 장착 중인 아이템 (slot -> Item 객체)
    # 기본 슬롯: main_hand(무기), body(갑옷), ring(반지)
    equipment: Dict[str, Optional[object]] = field(default_factory=lambda: {
        "main_hand": None,
        "body": None,
        "ring": None
    })