import sys
import os

print("LOG: 진단 스크립트 시작")

# 1. 경로 설정 확인
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
    sys.path.insert(0, PROJECT_ROOT)
    print(f"LOG: 경로 설정 완료 (Root: {PROJECT_ROOT})")
except Exception as e:
    print(f"ERROR: 경로 설정 실패 - {e}")
    sys.exit()

# 2. 모듈별 임포트 테스트 (범인 색출)
print("LOG: 모듈 임포트 테스트 시작...")

try:
    print("  - Actor 모듈 로딩 중...", end="")
    from src.models.actor import Actor
    print(" [성공]")
except Exception as e:
    print(f" [실패]\nERROR: src/models/actor.py 파일에 문제가 있습니다.\n{e}")
    sys.exit()

try:
    print("  - GrowthSystem 모듈 로딩 중...", end="")
    from src.systems.growth_system import GrowthSystem
    print(" [성공]")
except Exception as e:
    print(f" [실패]\nERROR: src/systems/growth_system.py 파일에 문제가 있습니다.\n{e}")
    sys.exit()

try:
    print("  - EntityFactory 모듈 로딩 중...", end="")
    from src.core.factory import EntityFactory
    print(" [성공]")
except Exception as e:
    print(f" [실패]\nERROR: src/core/factory.py 파일에 문제가 있습니다.\n{e}")
    sys.exit()

# 3. 기능 실행 테스트
print("LOG: 기능 실행 테스트 시작...")

try:
    print("  - 테스트용 Actor 생성 시도...", end="")
    # 팩토리를 거치지 않고 직접 생성하여 모델 문제인지 확인
    actor = Actor(id="test", name="DebugBot", race_id="human", class_id="warrior")
    print(" [성공]")
    
    print(f"  - 초기 매력(Charisma) 수치 확인: {actor.base_stats.get('charisma')}...", end="")
    if actor.base_stats.get('charisma') is None:
        print(" [경고: None]")
    else:
        print(" [성공]")

    print("  - GrowthSystem.refresh_stats 호출...", end="")
    # 여기서 멈춘다면 무한 루프 가능성 높음
    GrowthSystem.refresh_stats(actor)
    print(" [성공]")
    
    print(f"  - 최종 HP 확인: {actor.max_hp}")
    print(f"  - 최종 CHA 확인: {GrowthSystem.get_scaled_stat(actor, 'charisma')}")

except Exception as e:
    print(f"\nERROR: 실행 중 오류 발생 - {e}")
    import traceback
    traceback.print_exc()

print("LOG: 진단 종료")