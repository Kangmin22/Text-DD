# File: src/models/actor.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Actor:
    """
    DND TEXT RPG의 모든 생명체(Player, Monster, NPC)를 정의하는 핵심 데이터 모델.
    성능 최적화를 위한 Dirty Flag 패턴과 장비/인벤토리 시스템을 포함합니다.
    """
    # --- 기본 식별 정보 ---
    id: str
    name: str
    race_id: str
    class_id: str
    
    # --- 성장 데이터 ---
    level: int = 1
    exp: int = 0
    
    # --- 실시간 리소스 ---
    current_hp: int = 0
    max_hp: int = 0 
    current_mp: int = 0
    max_mp: int = 0
    
    # --- 능력치 (Base Stats) ---
    # 모든 기본 능력치는 10을 기준으로 시작합니다.
    # [Critical Fix] 매력(Charisma)이 누락되지 않도록 딕셔너리에 명시합니다.
    base_stats: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    })
    
    # --- 최적화용 필드 (Dirty Flag Pattern) ---
    # 스탯 계산 부하를 줄이기 위해 캐싱을 사용합니다.
    _cached_stats: Dict[str, int] = field(default_factory=dict)
    _is_stats_dirty: bool = True  # True일 때 GrowthSystem이 재계산을 수행합니다.
    
    # --- 전투 및 기술 ---
    keystones: Dict[str, bool] = field(default_factory=dict) # 활성화된 특화(Mastery)
    skills: List[str] = field(default_factory=list)         # 보유 스킬 ID 목록
    status_effects: List[Dict] = field(default_factory=list) # 현재 걸린 버프/디버프
    
    # --- 아이템 및 장비 ---
    inventory: List = field(default_factory=list)
    equipment: Dict[str, Optional[object]] = field(default_factory=lambda: {
        "main_hand": None,
        "body": None,
        "ring": None
    })
    
    def mark_dirty(self):
        """
        장비 교체, 레벨업, 버프 획득 등 스탯 변화가 발생할 때 호출하여
        다음번 스탯 참조 시 재계산이 일어나도록 유도합니다.
        """
        self._is_stats_dirty = True

    def __post_init__(self):
        """객체 생성 직후 기본 설정을 수행합니다."""
        # 초기 생성 시 누락된 필드가 없도록 보장합니다.
        for stat in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            if stat not in self.base_stats:
                self.base_stats[stat] = 10