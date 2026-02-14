# File: src/models/item.py
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Item:
    """
    게임 내 존재하는 모든 아이템(장비, 소모품 등)의 데이터 모델.
    """
    id: str
    name: str
    type: str  # "weapon", "armor", "accessory"
    slot: str  # "main_hand", "body", "ring"
    
    # 장착 시 오르는 스탯 (예: {"strength": 5, "max_hp": 50})
    bonus_stats: Dict[str, int] = field(default_factory=dict)
    
    # 아이템 설명
    description: str = ""
    
    # 가격
    price: int = 0