import random
from src.systems.growth_system import GrowthSystem

class MathEngine:
    """
    게임 내 모든 수치 연산을 담당하는 핵심 엔진입니다.
    Version: v2.2 (Final Balanced - 시뮬레이션 검증 완료)

    [핵심 연산 로직]
    1. 데미지 산출: 스킬 계수(Scaling)를 AP/SP에 곱하여 합산.
    2. 명중/회피: 민첩(DEX) 기반 회피율 판정 (마법은 필중).
    3. 치명타: 민첩 기반 확률 판정 및 1.5배 가중치 부여.
    4. 방어력: 체질(CON) 기반의 퍼센트 데미지 감소(DR) 적용.
    """

    @staticmethod
    def calculate_skill_damage(attacker, defender, skill_data: dict) -> tuple[int, bool]:
        """
        공격자의 능력치와 기술 데이터를 기반으로 최종 피해량과 치명타 여부를 결정합니다.
        공식: ((AP * ap_계수) + (SP * sp_계수)) * (분산) * (치명타) * (1 - 방어율)
        """
        # 1. 공격자의 실시간 공격력(AP/SP) 확보
        ap = GrowthSystem.get_attack_power(attacker)
        sp = GrowthSystem.get_magic_power(attacker)
        
        # 2. 기술의 계수(Scaling) 정보 추출 (기본값은 평타 계수 1.0)
        scaling = skill_data.get("scaling", {"ap": 1.0, "sp": 0.0})
        ap_coef = scaling.get("ap", 0.0)
        sp_coef = scaling.get("sp", 0.0)
        
        # 기본 데미지 합계 계산
        base_damage = (ap * ap_coef) + (sp * sp_coef)
        
        # 3. 데미지 분산 적용 (±10% 범위의 난수)
        # 매번 일정한 데미지가 아닌 '주사위 굴림'의 느낌을 줍니다.
        variance = random.uniform(0.9, 1.1)
        varied_damage = base_damage * variance
        
        # 4. 치명타(Critical) 판정
        # 민첩(DEX) 10 기준 5% 확률, DEX 1포인트당 0.5%씩 추가 확률 부여
        attacker_dex = GrowthSystem.get_scaled_stat(attacker, "dexterity")
        crit_chance = 0.05 + max(0, (attacker_dex - 10) * 0.005)
        
        is_crit = False
        if random.random() < crit_chance:
            is_crit = True
            varied_damage *= 1.5 # 치명타 발생 시 데미지 50% 증폭
            
        # 5. 방어력(Damage Reduction) 적용
        # 스킬 타입에 따라 방어구 관통 여부 결정
        skill_type = skill_data.get("type", "physical")
        defense_rate = GrowthSystem.get_defense(defender)
        
        # 물리(physical)와 하이브리드(hybrid)는 적의 방어력에 영향을 받음
        if skill_type in ["physical", "hybrid"]:
            final_damage = varied_damage * (1.0 - defense_rate)
        else:
            # 순수 마법(magic)은 적의 물리 방어력을 무시 (트루 데미지)
            # 마법 저항력 시스템 도입 전까지는 마법이 방어 무시로 작동하여 강력함을 유지
            final_damage = varied_damage
            
        return max(1, int(final_damage)), is_crit

    @staticmethod
    def roll_hit(attacker, defender, skill_data: dict) -> bool:
        """
        공격의 명중 여부를 판정합니다.
        - 마법(magic): 주문력의 특성상 피하기 어려우므로 필중(True).
        - 그 외: 방어자의 민첩(DEX)에 따른 회피율(Evasion)을 주사위와 비교.
        """
        skill_type = skill_data.get("type", "physical")
        
        # 마법 스킬은 빗나가지 않음 (전략적 가치 제고)
        if skill_type == "magic":
            return True
            
        # 방어자의 실시간 회피율 가져오기
        evasion_chance = GrowthSystem.get_evasion(defender)
        
        # 0.0 ~ 1.0 사이의 주사위를 굴림
        hit_roll = random.random()
        
        # 주사위 눈금이 회피율보다 높으면 명중 성공
        # 예: 회피율 15%(0.15)일 때, 주사위가 0.15 미만이면 '피함' 판정
        return hit_roll >= evasion_chance