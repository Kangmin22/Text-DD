# File: src/models/actor.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Actor:
    """
    RPG 핵심 데이터를 포함하도록 확장된 액터 모델.
    """
    id: str
    name: str
    race_id: str
    class_id: str
    
    level: int = 1
    exp: int = 0
    
    # 리소스 (실시간 변동)
    current_hp: int = 0
    max_hp: int = 0 
    current_mp: int = 0
    max_mp: int = 0
    
    # 기본 능력치 (Base)
    base_stats: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10
    })
    
    # 특수 특성 및 스킬
    keystones: Dict[str, bool] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list) # 스킬 ID 리스트
    
    # 상태 이상 및 효과 (Active Effects)
    # 각 효과는 { "id": "poison", "duration": 3, "value": 5 } 식의 데이터
    status_effects: List[Dict] = field(default_factory=list)

    # 인벤토리 및 장비
    inventory: List = field(default_factory=list)
    equipment: Dict[str, Optional[object]] = field(default_factory=lambda: {
        "main_hand": None,
        "body": None,
        "ring": None
    })