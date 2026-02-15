# File: src/utils/data_loader.py
import json
import os
from typing import Dict, Any, Optional

class DataLoader:
    """
    src/data/ 경로의 JSON 데이터들을 로드하고 캐싱하는 유틸리티 클래스.
    """
    _cache: Dict[str, Any] = {}

    @staticmethod
    def _get_data_path(filename: str) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # src/utils -> src -> data 로 이동
        return os.path.abspath(os.path.join(base_dir, "../data", filename))

    @staticmethod
    def load_json(filename: str) -> Dict[str, Any]:
        if filename in DataLoader._cache:
            return DataLoader._cache[filename]

        path = DataLoader._get_data_path(filename)
        if not os.path.exists(path):
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                DataLoader._cache[filename] = data
                return data
        except (json.JSONDecodeError, IOError):
            return {}

    @staticmethod
    def load_race(race_id: str) -> Optional[Dict[str, Any]]:
        data = DataLoader.load_json("races.json")
        return data.get(race_id)

    @staticmethod
    def load_class(class_id: str) -> Optional[Dict[str, Any]]:
        data = DataLoader.load_json("classes.json")
        return data.get(class_id)

    @staticmethod
    def load_item(item_id: str) -> Optional[Dict[str, Any]]:
        data = DataLoader.load_json("items.json")
        if data and item_id in data:
            item = data[item_id]
            item["id"] = item_id
            return item
        return None

    @staticmethod
    def load_skill(skill_id: str) -> Optional[Dict[str, Any]]:
        data = DataLoader.load_json("skills.json")
        return data.get(skill_id)

    # [NEW] 몬스터 데이터 로드 추가
    @staticmethod
    def load_monster(monster_id: str) -> Optional[Dict[str, Any]]:
        data = DataLoader.load_json("monsters.json")
        return data.get(monster_id)