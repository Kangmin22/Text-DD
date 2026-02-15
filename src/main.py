import sys
import os

# --- 경로 설정 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.engine import GameEngine
from src.states.title_state import TitleState

# =================================================================================
# 메인 실행 블록
# =================================================================================
if __name__ == "__main__":
    # 게임 엔진을 초기화하고 타이틀 화면으로 시작합니다.
    app = GameEngine()
    app.state_machine.change(TitleState())
    app.run()