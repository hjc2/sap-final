
from typing import Optional, List, Tuple, Dict
from collections import defaultdict
from core import GameState, Team, Phase, TriggerType, Pet

# after progress report, decided against game tree exploration, removed it
class BattleSimulator:
    def __init__(self, deterministic: bool = False, seed: Optional[int] = None):
        self.deterministic = deterministic
        self.seed = seed
        if seed is not None:
            import random
            random.seed(seed)

    def simulate_battle(self, team1: Team, team2: Team) -> GameState:
        # run a battle
        state = GameState(team1=team1.copy(), team2=team2.copy())

        # start of battle triggers
        self._trigger_phase(state, TriggerType.START_OF_BATTLE)

        self._process_faints(state)

        # main battle loop
        while not state.is_terminal:
            self._battle_turn(state)

            # check for winner
            winner = state.check_winner()
            if winner is not None:
                state.winner = winner
                state.is_terminal = True

        return state

    def _battle_turn(self, state: GameState):
        # single turn
        state.turn_number += 1

        # get front pets
        pet1 = state.team1.get_front_pet()
        pet2 = state.team2.get_front_pet()

        if not pet1 or not pet2:
            return

        # before attack triggers
        state.phase = Phase.BEFORE_ATTACK
        self._trigger_phase(state, TriggerType.BEFORE_ATTACK)

        # attack phase
        state.phase = Phase.ATTACK
        self._execute_attack(state, pet1, pet2)

        # after attack triggers
        state.phase = Phase.AFTER_ATTACK
        self._trigger_phase(state, TriggerType.AFTER_ATTACK)

        # process faints
        self._process_faints(state)

    def _execute_attack(self, state: GameState, pet1: Pet, pet2: Pet):
        # simultaneous attack
        damage1 = pet1.attack
        damage2 = pet2.attack

        # trigger FRIEND_AHEAD_ATTACKS before dealing damage
        self._check_friend_ahead_attacks(state, pet1, state.team1)
        self._check_friend_ahead_attacks(state, pet2, state.team2)

        pet1.take_damage(damage2)
        pet2.take_damage(damage1)

    def _process_faints(self, state: GameState):
        fainted_pets = []

        # check ALL pets (not just alive ones) to find newly fainted pets
        for pet in [p for p in state.team1.pets if p]:
            if pet.health <= 0 and not pet.is_fainted:
                pet.is_fainted = True
                fainted_pets.append((pet, state.team1))

        for pet in [p for p in state.team2.pets if p]:
            if pet.health <= 0 and not pet.is_fainted:
                pet.is_fainted = True
                fainted_pets.append((pet, state.team2))

        # trigger faint abilities
        for pet, team in fainted_pets:
            if pet.trigger_type == TriggerType.FAINT and pet.ability:
                pet.ability(state, pet, team)

    def _trigger_phase(self, state: GameState, trigger_type: TriggerType):
        # collect all pets with this trigger from both teams
        team1_pets = [(pet, state.team1) for pet in state.team1.get_alive_pets()
                      if pet.trigger_type == trigger_type and pet.ability]
        team2_pets = [(pet, state.team2) for pet in state.team2.get_alive_pets()
                      if pet.trigger_type == trigger_type and pet.ability]

        # interleave triggers by position to ensure fairness
        # process position 0 from both teams, then position 1 from both teams, etc.
        max_len = max(len(team1_pets), len(team2_pets))

        for i in range(max_len):
            # trigger team 1 pet at this position
            if i < len(team1_pets):
                pet, team = team1_pets[i]
                pet.ability(state, pet, team)

            # trigger team 2 pet at this position
            if i < len(team2_pets):
                pet, team = team2_pets[i]
                pet.ability(state, pet, team)

    # not used bc tier 1 pets
    def _check_friend_ahead_attacks(self, state: GameState, attacker: Pet, team: Team):
        # check if friend behind has attack trigger
        if attacker.position is None:
            return

        # check all pets behind the attacker
        for pet in team.get_alive_pets():
            if pet.position is not None and pet.position > attacker.position:
                if pet.trigger_type == TriggerType.FRIEND_AHEAD_ATTACKS and pet.ability:
                    pet.ability(state, pet, team)

    # does k battles
    def k_battles(self, team1: Team, team2: Team, num_simulations: int = 1000) -> Dict:

        stats = defaultdict(int)
        stats['total_simulations'] = num_simulations
        stats['team1_wins'] = 0
        stats['team2_wins'] = 0
        stats['draws'] = 0

        for _ in range(num_simulations):
            result = self.simulate_battle(team1, team2)

            if result.winner == 1:
                stats['team1_wins'] += 1
            elif result.winner == 2:
                stats['team2_wins'] += 1
            elif result.winner == 0:
                stats['draws'] += 1
            else:
                raise Exception("battle result not in {0,1,2}")
        
        stats['team1_win_rate'] = (stats['team1_wins'] / num_simulations) * 100
        stats['team2_win_rate'] = (stats['team2_wins'] / num_simulations) * 100
        stats['draw_rate'] = (stats['draws'] / num_simulations) * 100

        return dict(stats)