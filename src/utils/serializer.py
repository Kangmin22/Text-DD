# src/utils/serializer.py
import json
import os
from typing import List, Dict, Any, Type

class Serializer:
    """
    게임 데이터를 JSON으로 직렬화/역직렬화하는 유틸리티.
    """

    @staticmethod
    def save_to_file(filepath: str, data: Dict[str, Any]) -> bool:
        """딕셔너리 데이터를 JSON 파일로 저장"""
        try:
            # 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"[System] Game saved to {filepath}")
            return True
        except Exception as e:
            print(f"[Error] Failed to save file: {e}")
            return False

    @staticmethod
    def load_from_file(filepath: str) -> Dict[str, Any]:
        """JSON 파일을 읽어 딕셔너리로 반환"""
        if not os.path.exists(filepath):
            print(f"[System] No save file found at {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Failed to load file: {e}")
            return None

    @staticmethod
    def encode_state_stack(stack: List[Any]) -> List[Dict[str, Any]]:
        """
        [StateObj1, StateObj2] -> [{"class": "TitleState", "data": {}}, ...]
        상태 객체 스택을 저장 가능한 JSON 리스트로 변환
        """
        serialized = []
        for state in stack:
            state_data = {
                "class": state.__class__.__name__,
                "context": getattr(state, "context", {}) # 상태가 가진 로컬 데이터(context) 저장
            }
            serialized.append(state_data)
        return serialized

    @staticmethod
    def decode_state_stack(data_list: List[Dict[str, Any]], state_map: Dict[str, Type]) -> List[Any]:
        """
        [{"class": "TitleState", ...}] -> [TitleState(), ...]
        저장된 데이터를 실제 상태 객체 스택으로 복구
        """
        stack = []
        for item in data_list:
            class_name = item["class"]
            context = item.get("context", {})
            
            if class_name in state_map:
                state_class = state_map[class_name]
                state_instance = state_class()
                state_instance.context = context # 데이터 복구
                stack.append(state_instance)
            else:
                print(f"[Warning] Unknown state class: {class_name}")
        return stack