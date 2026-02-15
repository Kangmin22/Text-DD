import uuid
from typing import Optional
from src.models.actor import Actor
from src.models.item import Item
from src.utils.data_loader import DataLoader
from src.systems.growth_system import GrowthSystem

class EntityFactory:
    """
    Actor 및 Item 생성을 전담하는 공장 클래스.
    """
    
    @staticmethod
    def create_player(name: str, race_id: str, class_id: str) -> Actor:
        # 기존 코드 유지...
        new_actor = Actor(
            id=str(uuid.uuid4()),
            name=name, 
            race_id=race_id, 
            class_id=class_id
        )

        race_data = DataLoader.load_race(race_id)
        if race_data:
            for stat, value in race_data.get("base_stats", {}).items():
                new_actor.base_stats[stat] = new_actor.base_stats.get(stat, 0) + value
        
        class_data = DataLoader.load_class(class_id)
        if class_data:
            for stat, value in class_data.get("base_stats", {}).items():
                new_actor.base_stats[stat] = new_actor.base_stats.get(stat, 0) + value
            
            new_actor.skills = class_data.get("initial_skills", [])
            for keystone in class_data.get("keystones", []):
                new_actor.keystones[keystone] = True

        new_actor.level = 1
        GrowthSystem.refresh_stats(new_actor)
        return new_actor

    # [NEW] 몬스터 생성 메서드 추가
    @staticmethod
    def create_monster(monster_id: str) -> Optional[Actor]:
        data = DataLoader.load_monster(monster_id)
        if not data:
            print(f"[Factory] Error: Monster ID '{monster_id}' not found.")
            return None
            
        # 몬스터 이름에 (Monster) 접미사 등을 붙여 구분할 수도 있음
        new_monster = Actor(
            id=str(uuid.uuid4()),
            name=data["name"],
            race_id="monster",
            class_id="monster"
        )
        
        # 1. 기본 스탯 적용
        new_monster.base_stats = data["base_stats"]
        
        # 2. 레벨 설정 (Challenge Rating 기반)
        new_monster.level = data.get("level", 1)
        
        # 3. 스탯 재계산 (GrowthSystem이 레벨에 맞춰 HP/MP 뻥튀기)
        GrowthSystem.refresh_stats(new_monster)
        
        return new_monster

    @staticmethod
    def create_item(item_id: str) -> Optional[Item]:
        # 기존 코드 유지...
        data = DataLoader.load_item(item_id)
        if not data: return None
        return Item(
            id=data.get("id", item_id),
            name=data["name"],
            type=data["type"],
            slot=data["slot"],
            bonus_stats=data.get("bonus_stats", {}),
            description=data.get("description", ""),
            price=data.get("price", 0)
        )