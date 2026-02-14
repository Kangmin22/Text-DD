# File: src/config.py
# 게임의 전역 설정 및 상수를 관리합니다.

import os

# --- 디버그 설정 ---
DEBUG_MODE = True  # 상세 로그 출력 여부

# --- 파일 경로 설정 ---
# 현재 파일(src/config.py)을 기준으로 프로젝트 루트를 찾습니다.
# abspath(__file__) -> .../src/config.py
# dirname(...)      -> .../src
# dirname(...)      -> .../ (Project Root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# [Critical] Phase 2에서 추가된 데이터 경로
DATA_DIR = os.path.join(BASE_DIR, 'src', 'data')

# 저장 경로
SAVE_DIR = os.path.join(BASE_DIR, 'saves')
SAVE_FILENAME = "savegame.json"
SAVE_PATH = os.path.join(SAVE_DIR, SAVE_FILENAME)

# --- 게임 밸런스 상수 (v9.0 기반) ---
GLOBAL_DAMAGE_SCALE = 0.50
MAX_LEVEL = 50