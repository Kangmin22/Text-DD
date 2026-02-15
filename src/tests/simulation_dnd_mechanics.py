import sys
import os
import time
import random

# 프로젝트 루트 경로 추가
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
sys.path.insert(0, PROJECT_ROOT)

from src.core.factory import EntityFactory
from src.systems.growth_system import GrowthSystem
from src.systems.combat_system import CombatSystem
from src.systems.math_engine import MathEngine
from src.utils.data_loader import DataLoader

def print_header(text):
    print("\n" + "="*85)
    print(f"{text:^85}")
    print("="*85)

def print_actor_stats(actor, label="Actor"):
    hp = actor.max_hp
    mp = actor.max_mp
    atk = GrowthSystem.get_attack_power(actor)
    defense = int(GrowthSystem.get_defense(actor) * 100)
    evasion = int(GrowthSystem.get_evasion(actor) * 100)
    
    str_v = GrowthSystem.get_scaled_stat(actor, "strength")
    int_v = GrowthSystem.get_scaled_stat(actor, "intelligence")
    
    print(f"📊 [{label}] {actor.name} (Lv.{actor.level} {actor.race_id}/{actor.class_id})")
    print(f"   ❤️ HP: {hp} | 💧 MP: {mp}")
    print(f"   ⚔️ ATK: {atk} (STR {str_v}) | ✨ MATK: {GrowthSystem.get_magic_power(actor)} (INT {int_v})")
    print(f"   🛡️ DEF: {defense}% | 💨 EVA: {evasion}%")
    print(f"   📜 Skills: {actor.skills}")

def assign_monster_skills(monster):
    """시뮬레이션용: 몬스터 ID에 따라 스킬 세팅"""
    mid = monster.name.lower() # 몬스터 이름 기준 (불곰, 매머드 등)
    if "불곰" in mid or "bear" in mid:
        monster.skills = ["basic_attack", "wild_bite"]
    elif "매머드" in mid or "mammoth" in mid:
        monster.skills = ["basic_attack", "crushing_stomp"]
    elif "워그" in mid or "worg" in mid:
        monster.skills = ["basic_attack", "wild_bite"]
    else:
        monster.skills = ["basic_attack"]

def run_duel(player, monster_id, monster_level_override=None, lethality_boost=1.5):
    """
    고도화된 스킬 기반 전투 시뮬레이션
    """
    monster = EntityFactory.create_monster(monster_id)
    if not monster:
        print(f"❌ 몬스터 데이터 없음: {monster_id}")
        return

    if monster_level_override:
        monster.level = monster_level_override
        GrowthSystem.refresh_stats(monster)

    # 몬스터 스킬 할당
    assign_monster_skills(monster)

    player.current_hp, player.current_mp = player.max_hp, player.max_mp
    monster.current_hp, monster.current_mp = monster.max_hp, monster.max_mp

    print("-" * 85)
    print(f"⚔️  SKILL-BASED BATTLE: {player.name} VS {monster.name} (Boost: x{lethality_boost})")
    print("-" * 85)
    
    print_actor_stats(player, "PLAYER")
    print_actor_stats(monster, "ENEMY")
    print("-" * 85)

    ctx = CombatSystem.initialize_combat([player], [monster])
    
    turn = 1
    p_total_dmg = 0
    m_total_dmg = 0
    p_skills_used = {}
    m_skills_used = {}

    while not ctx.is_finished and turn <= 100:
        current_id = ctx.turn_order[ctx.current_turn_index]
        attacker = player if current_id == player.id else monster
        defender = monster if current_id == player.id else player
        
        # --- [AI 로직] ---
        # 1. 사용 가능한 액티브 스킬 목록 추출
        active_skills = [s for s in attacker.skills if s != "basic_attack"]
        skill_id = "basic_attack"
        
        for s_id in active_skills:
            s_data = DataLoader.load_skill(s_id)
            if not s_data: continue
            cost = s_data.get("cost", {}).get("mp", 0)
            if attacker.current_mp >= cost:
                # 40% 확률로 스킬 사용 (너무 남발하지 않게)
                if random.random() < 0.4:
                    skill_id = s_id
                    break
        
        # 데미지 기록용
        pre_hp = defender.current_hp
        
        # 전투 실행
        CombatSystem.process_action(attacker, defender, skill_id, ctx)
        
        # Lethality Boost 적용
        dmg_done = pre_hp - defender.current_hp
        if lethality_boost > 1.0:
            extra = int(dmg_done * (lethality_boost - 1.0))
            defender.current_hp = max(0, defender.current_hp - extra)
            dmg_done += extra

        # 통계 기록
        if current_id == player.id:
            p_total_dmg += dmg_done
            p_skills_used[skill_id] = p_skills_used.get(skill_id, 0) + 1
        else:
            m_total_dmg += dmg_done
            m_skills_used[skill_id] = m_skills_used.get(skill_id, 0) + 1

        # 매 턴 MP 소량 회복 (지능/지혜 밸런싱)
        attacker.current_mp = min(attacker.max_mp, attacker.current_mp + 2)

        if ctx.combat_logs:
            print(f"   [T{turn}] {attacker.name:12} -> {skill_id:15} : {ctx.combat_logs[-1]}")

        if defender.current_hp <= 0:
            print(f"\n🏆 승리자: {attacker.name} (종료 턴: {turn})")
            break

        ctx.current_turn_index = (ctx.current_turn_index + 1) % len(ctx.turn_order)
        if ctx.current_turn_index == 0: turn += 1

    # === 리포트 출력 ===
    print("\n📝 [전투 분석 결과]")
    print(f"   - 총 누적 데미지: 플레이어({p_total_dmg}) / 몬스터({m_total_dmg})")
    print(f"   - 플레이어 스킬 기록: {p_skills_used}")
    print(f"   - 몬스터 스킬 기록: {m_skills_used}")
    
    p_ttk = player.max_hp / (m_total_dmg / turn if turn > 0 else 1)
    m_ttk = monster.max_hp / (p_total_dmg / turn if turn > 0 else 1)
    print(f"   - 실제 생존력(TTK): 플레이어({p_ttk:.1f}턴) / 몬스터({m_ttk:.1f}턴)")
    
    if p_ttk < 5: verdict = "🔴 너무 매움 (HP 상향 필요)"
    elif p_ttk > 10: verdict = "🔵 싱거움 (데미지 상향 필요)"
    else: verdict = "🟢 훌륭함 (전략적인 긴장감)"
    
    print(f"   - 최종 평점: {verdict}")
    print("=" * 85)

def run_simulation():
    print_header("D&D ABYSS WALKER - INTELLIGENT COMBAT SIMULATOR")
    
    # [Case 1] 1레벨 초보자 vs 불곰 (짐승의 습격)
    p1 = EntityFactory.create_player("Novice", "human", "fighter")
    p1.skills = ["basic_attack", "power_strike"]
    run_duel(p1, "brown_bear", monster_level_override=1, lethality_boost=1.5)

    # [Case 2] 10레벨 영웅 vs 매머드 (거대수의 포효)
    p2 = EntityFactory.create_player("Legend", "dragonborn", "paladin")
    p2.skills = ["basic_attack", "holy_strike"]
    p2.level = 10
    GrowthSystem.refresh_stats(p2)
    run_duel(p2, "mammoth", monster_level_override=10, lethality_boost=1.5)

if __name__ == "__main__":
    run_simulation()