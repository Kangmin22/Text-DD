# File: src/utils/data_loader.py
import json
import os
from typing import Dict, Any, Optional
from src.config import DATA_DIR

class DataLoader:
    """
    JSON 데이터 파일을 로드하여 파이썬 딕셔너리로 변환하는 유틸리티 클래스.
    캐싱(Caching)을 통해 파일을 매번 다시 읽지 않도록 최적화합니다.
    """
    _cache: Dict[str, Any] = {}

    @staticmethod
    def _load_json(filename: str) -> Any:
        if filename in DataLoader._cache:
            return DataLoader._cache[filename]

        file_path = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"[System] Warning: 데이터 파일을 찾을 수 없습니다. ({file_path})")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                DataLoader._cache[filename] = data
                return data
        except json.JSONDecodeError as e:
            print(f"[System] Error: JSON 파일 파싱 실패 ({filename}): {e}")
            return None

    @staticmethod
    def load_race(race_id: str) -> Optional[Dict]:
        races_data = DataLoader._load_json("races.json")
        return races_data.get(race_id) if races_data else None

    @staticmethod
    def load_class(class_id: str) -> Optional[Dict]:
        classes_data = DataLoader._load_json("classes.json")
        return classes_data.get(class_id) if classes_data else None

    # [New] 아이템 데이터 로드 기능 추가
    @staticmethod
    def load_item(item_id: str) -> Optional[Dict]:
        """
        items.json을 읽고, 특정 item_id에 해당하는 정보를 반환합니다.
        """# File: src/utils/data_loader.py
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
        # 파일의 절대 경로를 기준으로 src/data 디렉토리 경로 계산
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base_dir, "../data", filename))

    @staticmethod
    def load_json(filename: str) -> Dict[str, Any]:
        """JSON 파일을 로드하고 캐싱합니다."""
        if filename in DataLoader._cache:
            return DataLoader._cache[filename]

        path = DataLoader._get_data_path(filename)
        if not os.path.exists(path):
            # 파일이 없을 경우 빈 딕셔너리 반환 및 경고 (로그 생략 가능)
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
        """종족 데이터를 반환합니다."""
        data = DataLoader.load_json("races.json")
        return data.get(race_id)

    @staticmethod
    def load_class(class_id: str) -> Optional[Dict[str, Any]]:
        """직업 데이터를 반환합니다."""
        data = DataLoader.load_json("classes.json")
        return data.get(class_id)

    @staticmethod
    def load_item(item_id: str) -> Optional[Dict[str, Any]]:
        """아이템 데이터를 반환합니다."""
        data = DataLoader.load_json("items.json")
        return data.get(item_id)

    @staticmethod
    def load_skill(skill_id: str) -> Optional[Dict[str, Any]]:
        """스킬 데이터를 반환합니다. (새로 추가됨)"""
        data = DataLoader.load_json("skills.json")
        return data.get(skill_id)
        items_data = DataLoader._load_json("items.json")
        if items_data and item_id in items_data:
            # 딕셔너리에 id 필드를 명시적으로 추가해서 리턴 (나중에 객체 만들 때 편함)
            item_info = items_data[item_id]
            item_info["id"] = item_id 
            return item_info
        else:
            print(f"[System] Warning: 아이템 ID '{item_id}'를 items.json에서 찾을 수 없습니다.")
            return None