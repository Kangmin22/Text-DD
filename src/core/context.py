from typing import Optional
from src.models.actor import Actor

class GameContext:
    """
    게임 전체에서 공유해야 하는 데이터를 관리하는 싱글톤 클래스입니다.
    기존의 global session_player를 대체합니다.
    """
    _instance = None
    player: Optional[Actor] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameContext, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_player(cls, player: Actor):
        cls.player = player

    @classmethod
    def get_player(cls) -> Optional[Actor]:
        return cls.player