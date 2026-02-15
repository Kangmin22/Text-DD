import time
from src.core.state_machine import State
from src.systems.combat_system import CombatSystem
from src.core.context import GameContext

class CombatState(State):
    def __init__(self, enemies: list):
        self.enemies = enemies

    def on_enter(self, prev_state=None):
        player = GameContext.get_player()
        print("\n" + "⚔️"*25)
        print("      전 투  시 작 !      ")
        print("⚔️"*25)
        
        self.ctx = CombatSystem.initialize_combat([player], self.enemies)

    def _draw_hp_bar(self, current, max_hp, length=15):
        if max_hp <= 0: max_hp = 1
        ratio = max(0, min(1, current / max_hp))
        filled = int(length * ratio)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {current}/{max_hp}"

    def update(self):
        if self.ctx.is_finished:
            if self.ctx.winner_side == "player":
                print(f"\n🏆 승리! 적들을 모두 처치했습니다.")
            else:
                print(f"\n💀 패배... 도망칩니다.")
            
            input(" (엔터키를 눌러 복귀) ")
            self.manager.pop()
            return

        player = self.ctx.participants[0]
        enemy = self.ctx.enemies[0] 

        print("\n" + "━"*50)
        print(f" [TURN {self.ctx.round_count}]")
        print(f" 🛡️  {player.name:<12} {self._draw_hp_bar(player.current_hp, player.max_hp)}")
        print(f" 🔥 {enemy.name:<12} {self._draw_hp_bar(enemy.current_hp, enemy.max_hp)}")
        print("━"*50)
        
        print(" [1] ⚔️ 기본 공격   [2] 💥 스킬 사용 (MP)   [3] 🛡️ 방어   [4] 🏃 도망")
        print(" 선택 >> ", end="")

    def handle_input(self, user_input: str):
        if self.ctx.is_finished: return

        player = self.ctx.participants[0]
        enemy = self.ctx.enemies[0]
        
        current_id = self.ctx.turn_order[self.ctx.current_turn_index]
        if current_id != player.id:
            self._process_ai_turns()
            return

        if user_input == '1':
            CombatSystem.process_action(player, enemy, "basic_attack", self.ctx)
        
        elif user_input == '2':
            active_skills = [s for s in player.skills if s != "basic_attack"]
            if active_skills:
                skill_to_use = active_skills[0] 
                CombatSystem.process_action(player, enemy, skill_to_use, self.ctx)
            else:
                print("\n ⚠️ 사용할 수 있는 스킬이 없습니다! (기본 공격만 보유)")
                return
        
        elif user_input == '3':
            heal = int(player.max_hp * 0.1)
            player.current_hp = min(player.max_hp, player.current_hp + heal)
            self.ctx.add_log(f"🛡️ {player.name} 방어 태세! 체력 {heal} 회복.")
        
        elif user_input == '4':
            print("💨 꽁무니가 빠지게 도망칩니다!")
            self.manager.pop()
            return
        
        else:
            print("\n ❌ 올바른 숫자를 입력하세요.")
            return

        print()
        for log in self.ctx.combat_logs[-2:]:
            print(f"  {log}")
            time.sleep(0.3)
        
        self._next_turn()
        self._process_ai_turns()

    def _next_turn(self):
        self.ctx.current_turn_index = (self.ctx.current_turn_index + 1) % len(self.ctx.turn_order)
        if self.ctx.current_turn_index == 0:
            self.ctx.round_count += 1

    def _process_ai_turns(self):
        while not self.ctx.is_finished:
            current_id = self.ctx.turn_order[self.ctx.current_turn_index]
            player = self.ctx.participants[0]

            if current_id == player.id:
                break
            
            enemy = next((e for e in self.ctx.enemies if e.id == current_id), None)
            if enemy:
                print(f"\n🤖 {enemy.name}의 턴...")
                time.sleep(0.5)
                skill = enemy.skills[0] if enemy.skills else "basic_attack"
                CombatSystem.process_action(enemy, player, skill, self.ctx)
                print(f"  🔥 {self.ctx.combat_logs[-1]}")
                time.sleep(0.5)

            if player.current_hp <= 0:
                self.ctx.is_finished = True
                self.ctx.winner_side = "enemy"
                break
                
            self._next_turn()