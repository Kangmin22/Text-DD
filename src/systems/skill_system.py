# File: src/systems/skill_system.py
from typing import Dict, Any, Optional
from src.models.actor import Actor
from src.systems.growth_system import GrowthSystem
from src.utils.data_loader import DataLoader

class SkillSystem:
    """
    스킬의 실행, 자원 소모 체크, 최종 데미지 계산을 담당하는 시스템.
    """

    @staticmethod
    def calculate_skill_damage(actor: Actor, skill_id: str) -> Dict[str, Any]:
        """
        액터가 특정 스킬을 사용할 때 발생하는 최종 데미지와 속성을 계산합니다.
        """
        # 1. 스킬 데이터 로드
        skill_data = DataLoader.load_skill(skill_id)
        if not skill_data:
            return {"damage": 0, "type": "none", "error": "Skill not found"}

        # 2. 자원 소모 체크 (여기서는 계산만 하고 실제 소모는 전투 시스템에서 처리)
        cost = skill_data.get("cost", {})
        if actor.current_mp < cost.get("mp", 0):
            return {"damage": 0, "type": "none", "error": "Insufficient MP"}
        if actor.current_hp < cost.get("hp", 0):
            return {"damage": 0, "type": "none", "error": "Insufficient HP"}

        # 3. 공격력(AP) 및 주문력(SP) 획득
        ap = GrowthSystem.get_attack_power(actor)
        sp = GrowthSystem.get_magic_power(actor)

        # 4. 스케일링 적용
        scaling = skill_data.get("scaling", {"ap": 1.0, "sp": 0.0})
        base_damage = (ap * scaling.get("ap", 0)) + (sp * scaling.get("sp", 0))

        # 5. 분산도 적용 (기본 5% 내외의 랜덤성)
        # 실제 구현시에는 random 모듈을 사용하나 시뮬레이션에서는 결정론적 결과 반환
        final_damage = int(base_damage)

        return {
            "skill_name": skill_data["name"],
            "damage": final_damage,
            "type": skill_data["type"],
            "cost": cost
        }

    @staticmethod
    def execute_skill(attacker: Actor, defender: Actor, skill_id: str) -> Dict[str, Any]:
        """
        스킬을 실제로 실행하고 결과를 반환합니다.
        (전투 로그 생성 및 상태 변경 포함 가능)
        """
        result = SkillSystem.calculate_skill_damage(attacker, skill_id)
        if "error" in result:
            return result

        # 마나/생명력 소모 적용
        attacker.current_mp -= result["cost"].get("mp", 0)
        attacker.current_hp -= result["cost"].get("hp", 0)

        # 방어자의 체력 감소 (여기서 방어 공식 적용 가능)
        # TODO: MathEngine.calculate_defense_dr 적용 예정
        defender.current_hp -= result["damage"]

        return result