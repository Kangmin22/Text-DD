# File: src/models/actor.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Actor:
    """
    RPG 핵심 데이터를 포함하는 액터 모델.
    최적화를 위한 캐싱 필드(_cached_stats, _is_stats_dirty)가 추가되었습니다.
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
    
    # --- 최적화용 캐시 필드 (Dirty Flag Pattern) ---
    # 외부에서 직접 접근하지 말고 시스템을 통해 접근해야 합니다.
    _cached_stats: Dict[str, int] = field(default_factory=dict)
    _is_stats_dirty: bool = True  # 생성 시 계산 필요
    
    # 특수 특성 및 스킬
    keystones: Dict[str, bool] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    
    # 상태 효과 (Status Effects)
    status_effects: List[Dict] = field(default_factory=list)

    # 인벤토리 및 장비
    inventory: List = field(default_factory=list)
    equipment: Dict[str, Optional[object]] = field(default_factory=lambda: {
        "main_hand": None,
        "body": None,
        "ring": None
    })
    
    def mark_dirty(self):
        """스탯 재계산이 필요함을 알립니다 (이벤트 발생 시 호출)."""
        self._is_stats_dirty = True