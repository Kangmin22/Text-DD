# File: src/core/factory.py
import uuid
from typing import Optional
from src.models.actor import Actor
from src.models.item import Item
from src.utils.data_loader import DataLoader
from src.systems.growth_system import GrowthSystem

class EntityFactory:
    """
    JSON 데이터와 파라미터를 조합하여 완성된 Actor 및 Item 객체를 생성하는 공장 클래스.
    """
    
    @staticmethod
    def create_player(name: str, race_id: str, class_id: str) -> Actor:
        # 1. 기본 Actor 객체 생성 (기본 스탯은 0으로 시작하여 데이터 로드 시 합산)
        new_actor = Actor(
            id=str(uuid.uuid4()),
            name=name, 
            race_id=race_id, 
            class_id=class_id
        )

        # 2. 종족(Race) 데이터 로드 및 적용 (종족 기본 보너스)
        race_data = DataLoader.load_race(race_id)
        if race_data:
            for stat, value in race_data.get("base_stats", {}).items():
                new_actor.base_stats[stat] = new_actor.base_stats.get(stat, 0) + value
        
        # 3. 직업(Class) 데이터 로드 및 적용
        class_data = DataLoader.load_class(class_id)
        if class_data:
            # 기본 스탯 합산
            for stat, value in class_data.get("base_stats", {}).items():
                new_actor.base_stats[stat] = new_actor.base_stats.get(stat, 0) + value
            
            # 초기 스킬 부여
            new_actor.skills = class_data.get("initial_skills", [])
            
            # 키스톤 활성화
            for keystone in class_data.get("keystones", []):
                new_actor.keystones[keystone] = True

        # 4. 초기 상태 설정 (레벨 1)
        new_actor.level = 1
        
        # 5. 최종 스탯 및 HP/MP 계산
        GrowthSystem.refresh_stats(new_actor)
        
        return new_actor

    @staticmethod
    def create_item(item_id: str) -> Optional[Item]:
        data = DataLoader.load_item(item_id)
        if not data:
            return None
            
        return Item(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            slot=data["slot"],
            bonus_stats=data.get("bonus_stats", {}),
            description=data.get("description", ""),
            price=data.get("price", 0)
        )