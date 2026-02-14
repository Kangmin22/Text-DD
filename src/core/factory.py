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
        new_actor = Actor(
            id=str(uuid.uuid4()),
            name=name, 
            race_id=race_id, 
            class_id=class_id
        )

        # 1. 종족(Race) 데이터 로드 및 적용
        race_data = DataLoader.load_race(race_id)
        if race_data:
            for stat, value in race_data.get("base_stats", {}).items():
                new_actor.base_stats[stat] = new_actor.base_stats.get(stat, 0) + value
        
        # 2. 직업(Class) 데이터 로드 및 적용
        class_data = DataLoader.load_class(class_id)
        if class_data:
            for stat, value in class_data.get("base_stats", {}).items():
                new_actor.base_stats[stat] = new_actor.base_stats.get(stat, 0) + value
            
            new_actor.skills = class_data.get("initial_skills", [])
            for keystone in class_data.get("keystones", []):
                new_actor.keystones[keystone] = True

        # 3. 초기 상태 설정 (레벨 1)
        new_actor.level = 1
        
        # 4. 최종 스탯 및 HP/MP 계산
        GrowthSystem.refresh_stats(new_actor)
        
        return new_actor

    @staticmethod
    def create_item(item_id: str) -> Optional[Item]:
        data = DataLoader.load_item(item_id)
        if not data:
            return None
            
        return Item(
            # JSON에 id가 없으면 키값(item_id)을 대신 사용
            id=data.get("id", item_id),
            name=data["name"],
            type=data["type"],
            slot=data["slot"],
            bonus_stats=data.get("bonus_stats", {}),
            description=data.get("description", ""),
            price=data.get("price", 0)
        )