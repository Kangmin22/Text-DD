# File: src/systems/combat_system.py
import random
from src.config import GLOBAL_DAMAGE_SCALE
from src.models.actor import Actor
from src.models.combat_context import CombatContext
from src.systems.math_engine import MathEngine, StatBucket
from src.systems.growth_system import GrowthSystem

class CombatSystem:
    """
    v10.0 강화된 전투 시스템: 플레이버 텍스트, 장비별 액션, 상태 이상 및 스킬 로직 통합.
    """
    
    # 밸런스 상수
    BASE_CRIT_MULT = 1.5
    MAX_CRIT_MULT = 2.5
    MAX_CRIT_CHANCE = 0.40
    CRIT_CHANCE_FACTOR = 0.012
    EVA_FACTOR = 0.55
    REFLECT_CAP = 0.25
    MIN_HIT_CHANCE = 0.60
    MASTERY_THRESHOLD = 20

    # --- 장비별 액션 동사 (Weapon Action Verbs) ---
    WEAPON_ACTIONS = {
        "rusty_greatsword": "묵직한 대검을 크게 휘둘러",
        "iron_dagger": "날카로운 단검으로 빈틈을 파고들어",
        "longbow": "시위를 당겨 화살을 날려",
        "default": "무기를 휘둘러"
    }

    # --- 플레이버 텍스트 모음 (시각 강조 포함) ---
    HIT_MESSAGES = [
        "{a}의 공격이 {d}에게 정통으로 꽂혔습니다!",
        "{a}이(가) {verb} {d}의 방어구를 울립니다.",
        "{a}의 기세가 {d}를 압도하며 타격을 입힙니다."
    ]
    
    CRIT_MESSAGES = [
        "💥 [ CRITICAL ] 💥 {a}의 일격이 {d}의 급소를 완벽하게 관통했습니다!!",
        "🔥 [ DESTRUCTIVE ] 🔥 {a}이(가) {verb} {d}에게 치명적인 충격을 줍니다!!",
        "⚡ [ EXPLOIT ] ⚡ {a}의 공격이 번뜩이며 {d}를 무력화시킵니다!!"
    ]
    
    MISS_MESSAGES = [
        "🍃 ( EVADE ) {d}이(가) {a}의 서툰 공격을 가볍게 피했습니다.",
        "❌ ( MISS ) {a}의 무기가 허공을 가르며 날카로운 소리만 남깁니다.",
        "🛡️ ( DEFLECT ) {d}이(가) {a}의 공격 궤적을 읽고 흘려보냈습니다."
    ]

    @staticmethod
    def get_masteries(stats: dict) -> dict:
        return {
            "RESOLUTE_TECHNIQUE": stats["strength"] >= CombatSystem.MASTERY_THRESHOLD,
            "DEADLY_ARTS": stats["dexterity"] >= CombatSystem.MASTERY_THRESHOLD,
            "IRON_FORTRESS": stats["constitution"] >= CombatSystem.MASTERY_THRESHOLD
        }

    @staticmethod
    def process_turn(ctx: CombatContext):
        attacker = ctx.get_current_attacker()
        defender = ctx.get_current_defender()

        # 1. 상태 이상 체크 (예: 기절)
        # Actor 모델에 status_effects 리스트가 있다고 가정 (없으면 빈 리스트)
        if hasattr(attacker, 'status_effects') and "stun" in attacker.status_effects:
            ctx.logs.append(f"🌀 {attacker.name}이(가) 기절하여 움직일 수 없습니다!")
            attacker.status_effects.remove("stun")
            ctx.turn_count += 1
            return

        a_stats = {s: GrowthSystem.get_scaled_stat(attacker, s) for s in ["strength", "dexterity", "constitution"]}
        d_stats = {s: GrowthSystem.get_scaled_stat(defender, s) for s in ["strength", "dexterity", "constitution"]}
        
        a_mastery = CombatSystem.get_masteries(a_stats)
        d_mastery = CombatSystem.get_masteries(d_stats)
        
        for k, v in attacker.keystones.items(): a_mastery[k] = a_mastery.get(k, False) or v
        for k, v in defender.keystones.items(): d_mastery[k] = d_mastery.get(k, False) or v

        # 장비 기반 동사 결정
        weapon = attacker.equipment.get("main_hand")
        verb = CombatSystem.WEAPON_ACTIONS.get(weapon.id if weapon else "default", CombatSystem.WEAPON_ACTIONS["default"])

        # --- [Step 1] 명중/회피 ---
        acc = a_stats["dexterity"] * 3.0 + a_stats["strength"] * 0.5
        eva = d_stats["dexterity"] * 2.0
        
        hit_chance = acc / (acc + (eva * CombatSystem.EVA_FACTOR)) if (acc + eva) > 0 else 0
        hit_chance = max(CombatSystem.MIN_HIT_CHANCE, hit_chance)
        
        if a_mastery["RESOLUTE_TECHNIQUE"] or d_mastery["IRON_FORTRESS"]: hit_chance = 1.0

        if random.random() > hit_chance:
            msg = random.choice(CombatSystem.MISS_MESSAGES).format(a=attacker.name, d=defender.name)
            ctx.logs.append(msg)
            ctx.turn_count += 1
            return

        # --- [Step 2] 스킬 트리거 (전사: 강타 등) ---
        skill_activated = False
        skill_bonus = 1.0
        if attacker.class_id == "warrior" and random.random() < 0.15:
            skill_activated = True
            skill_bonus = 1.5
            ctx.logs.append(f"⚔️ [SKILL: POWER STRIKE] {attacker.name}이(가) 온 힘을 모아 내리칩니다!")

        # --- [Step 3] 공격력 파이프라인 ---
        base_atk = a_stats["strength"] * 2.0 + a_stats["dexterity"] * 0.5
        bucket = StatBucket(base_atk)
        if a_mastery["RESOLUTE_TECHNIQUE"]: bucket.add_more(1.30)
        if a_mastery["DEADLY_ARTS"]:
            pen_rate = a_stats["dexterity"] / (a_stats["dexterity"] + 40)
            bucket.add_more(1.0 + pen_rate)

        raw_dmg = bucket.calculate() * GLOBAL_DAMAGE_SCALE * skill_bonus * random.uniform(0.95, 1.05)

        # --- [Step 4] 방어 감쇄 ---
        armor = d_stats["constitution"] * 1.5 + d_stats["strength"] * 0.2
        dr = MathEngine.calculate_defense_dr(armor, attacker.level)
        con_resilience = d_stats["constitution"] / (d_stats["constitution"] + 120)
        mitigated_dmg = raw_dmg * (1.0 - dr) * (1.0 - con_resilience)
        if d_mastery["IRON_FORTRESS"]: mitigated_dmg *= 0.90

        # --- [Step 5] 치명타 ---
        is_crit = False
        if not a_mastery["RESOLUTE_TECHNIQUE"]:
            crit_prob = min(CombatSystem.MAX_CRIT_CHANCE, a_stats["dexterity"] * CombatSystem.CRIT_CHANCE_FACTOR)
            if a_mastery["DEADLY_ARTS"]: crit_prob = min(0.80, a_stats["dexterity"] * CombatSystem.CRIT_CHANCE_FACTOR)
            
            if random.random() < crit_prob:
                is_crit = True
                crit_mult = CombatSystem.BASE_CRIT_MULT + (a_stats["dexterity"] * 0.015)
                mitigated_dmg *= min(CombatSystem.MAX_CRIT_MULT, crit_mult)

        # --- [Step 6] 피해 및 상태 이상 적용 ---
        final_dmg = int(max(1, mitigated_dmg))
        
        # 반사 데미지
        reflect_rate = min(CombatSystem.REFLECT_CAP, d_stats["constitution"] / (d_stats["constitution"] + 100))
        if d_mastery["IRON_FORTRESS"]: reflect_rate *= 1.5
        reflected_dmg = int(final_dmg * reflect_rate)
        if a_mastery["RESOLUTE_TECHNIQUE"]: reflected_dmg = 0

        defender.current_hp = max(0, defender.current_hp - final_dmg)
        attacker.current_hp = max(0, attacker.current_hp - reflected_dmg)

        # 상태 이상 확률 (DEX 비례 출혈 등)
        if a_mastery["DEADLY_ARTS"] and random.random() < 0.2:
            if not hasattr(defender, 'status_effects'): defender.status_effects = []
            if "bleed" not in defender.status_effects:
                defender.status_effects.append("bleed")
                ctx.logs.append(f"🩸 {defender.name}의 상처에서 피가 흐르기 시작합니다! (상태이상: 출혈)")

        # 로그 생성
        if is_crit:
            msg = random.choice(CombatSystem.CRIT_MESSAGES).format(a=attacker.name, d=defender.name, verb=verb)
        else:
            msg = random.choice(CombatSystem.HIT_MESSAGES).format(a=attacker.name, d=defender.name, verb=verb)
        
        ctx.logs.append(msg)
        ctx.logs.append(f"   ↳ 💢 {final_dmg}의 피해를 입혔습니다!")
        
        if reflected_dmg > 0:
            ctx.logs.append(f"   ↳ 🛡️ <<< REFLECT >>> {attacker.name}이(가) {reflected_dmg}의 피해를 되돌려받았습니다.")

        # 승패 판정
        if defender.current_hp <= 0:
            ctx.is_finished = True
            ctx.winner = attacker
            ctx.logs.append(f"\n✨ 승리! {defender.name}이(가) 비참한 최후를 맞이합니다.")
        elif attacker.current_hp <= 0:
            ctx.is_finished = True
            ctx.winner = defender
            ctx.logs.append(f"\n💀 패배... {attacker.name}이(가) 무릎을 꿇고 말았습니다.")
        else:
            ctx.turn_count += 1