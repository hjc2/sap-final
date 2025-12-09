
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from enum import Enum
import copy
import random

# times possible for triggers
class Phase(Enum):
    START_OF_BATTLE = "start_of_battle"
    BEFORE_ATTACK = "before_attack"
    ATTACK = "attack"
    AFTER_ATTACK = "after_attack"
    FAINT = "faint"
    END_OF_BATTLE = "end_of_battle"

# pet triggers
class TriggerType(Enum):
    START_OF_BATTLE = "start_of_battle" #mosquito
    BEFORE_ATTACK = "before_attack" #
    AFTER_ATTACK = "after_attack"
    HURT = "hurt"
    FAINT = "faint"
    FRIEND_SUMMONED = "friend_summoned"
    FRIEND_AHEAD_ATTACKS = "friend_ahead_attacks"
    FRIEND_AHEAD_FAINTS = "friend_ahead_faints"
    END_TURN = "end_turn"


@dataclass
class Pet:
    name: str
    attack: int
    health: int
    level: int = 1
    experience: int = 0
    ability: Optional[Callable] = None
    trigger_type: Optional[TriggerType] = None
    is_fainted: bool = False
    position: Optional[int] = None  # position in team

    def __repr__(self):
        status = "X" if self.is_fainted else ""
        return f"{self.name}({self.attack}/{self.health}){status}"

    def take_damage(self, damage: int) -> int:
        actual_damage = min(damage, self.health)
        self.health -= actual_damage
        if self.health <= 0:
            self.health = 0
            # let faint trigger happen
        return actual_damage

    def deal_damage_to(self, target: Pet) -> int:
        # damage another pet
        return target.take_damage(self.attack)

    def copy(self) -> Pet:
        #duplicate
        return copy.deepcopy(self)


@dataclass
class Team:
    # team structure
    pets: List[Optional[Pet]] = field(default_factory=lambda: [None] * 5)
    max_size: int = 5

    def __repr__(self):
        return f"Team({[p for p in self.pets if p]})"

    def get_alive_pets(self) -> List[Pet]:
        return [p for p in self.pets if p and not p.is_fainted]

    def get_front_pet(self) -> Optional[Pet]:
        for pet in self.pets:
            if pet and not pet.is_fainted:
                return pet
        return None

    def remove_pet(self, pet: Pet):
        for i, p in enumerate(self.pets):
            if p is pet:
                self.pets[i] = None
                break

    def get_pet_at(self, position: int) -> Optional[Pet]:
        if 0 <= position < len(self.pets):
            return self.pets[position]
        return None

    def add_pet(self, pet: Pet, position: Optional[int] = None) -> bool:
        # numerical name handler
        base_name = pet.name
        existing_names = []
        for p in self.pets:
            if p and not p.is_fainted:
                existing_names.append(p.name)
        if base_name in existing_names:
            counter = 2
            while f"{base_name}{counter}" in existing_names:
                counter += 1
            pet.name = f"{base_name}{counter}"

        if position is not None:
            if 0 <= position < self.max_size and self.pets[position] is None:
                self.pets[position] = pet
                pet.position = position
                return True
        else:
            for i in range(self.max_size):
                if self.pets[i] is None:
                    self.pets[i] = pet
                    pet.position = i
                    return True
        return False

    def add_pets(self, *pet_names: str) -> 'Team':
        # add multiple
        from pets import create_pet
        for name in pet_names:
            self.add_pet(create_pet(name))
        return self

    def copy(self) -> Team:
        # deep copy, probably legacy
        return copy.deepcopy(self)


@dataclass
class RandomChoice:
    ####### old random
    description: str
    options: List[Any]
    probabilities: Optional[List[float]] = None

    def __post_init__(self):
        if self.probabilities is None:
            # uniform distribution
            self.probabilities = [1.0 / len(self.options)] * len(self.options)


@dataclass
class GameState:
    # battle class
    team1: Team
    team2: Team
    phase: Phase = Phase.START_OF_BATTLE
    turn_number: int = 0
    pending_triggers: List[tuple] = field(default_factory=list)
    winner: Optional[int] = None  # 1, 2, or 0 for draw
    is_terminal: bool = False

    def copy(self) -> GameState:
        # deep copy
        return copy.deepcopy(self)

    def check_winner(self) -> Optional[int]:
        # check for winner
        team1_alive = len(self.team1.get_alive_pets()) > 0
        team2_alive = len(self.team2.get_alive_pets()) > 0

        if not team1_alive and not team2_alive:
            return 0  # draw
        elif not team2_alive:
            return 1  # team 1 wins
        elif not team1_alive:
            return 2  # team 2 wins
        return None

    def pretty_print(self):
        # pp game board
        print("-"*10)
        print(f"{'TEAM 1':^28} vs {'TEAM 2':^28}")
        print("-"*10)

        # get all pets (including None for empty slots)
        team1_pets = self.team1.pets
        team2_pets = self.team2.pets

        max_slots = max(len(team1_pets), len(team2_pets))

        # print each slot
        for i in range(max_slots):
            pet1 = team1_pets[i] if i < len(team1_pets) else None
            pet2 = team2_pets[i] if i < len(team2_pets) else None

            # format team 1 side
            if pet1 and not pet1.is_fainted:
                left_name = pet1.name[:12]  # truncate
                left_stats = f"({pet1.attack},{pet1.health})"
                left_side = f"{left_name:>12} {left_stats:>6}"
            elif pet1 and pet1.is_fainted:
                left_name = pet1.name[:12] # truncate
                left_stats = "X"
                left_side = f"{left_name:>12} {left_stats:>6}"
            else:
                left_side = f"{'---':>12} {'':>6}"

            # format team 2 side
            if pet2 and not pet2.is_fainted:
                right_name = pet2.name[:12] # truncate
                right_stats = f"({pet2.attack},{pet2.health})"
                right_side = f"{right_stats:<6} {right_name:<12}"
            elif pet2 and pet2.is_fainted:
                right_name = pet2.name[:12] # truncate
                right_stats = "X"
                right_side = f"{right_stats:<6} {right_name:<12}"
            else:
                right_side = f"{'':>6} {'---':<12}"

            # print the row with position indicator
            position_marker = "->" if i == 0 else f"{i}"
            print(f"[{position_marker}] {left_side}  |  {right_side}")

        print("-"*10)

        # print status
        team1_alive = len(self.team1.get_alive_pets())
        team2_alive = len(self.team2.get_alive_pets())
        print(f"Turn: {self.turn_number}  |  Alive: Team1={team1_alive}  Team2={team2_alive}")

        if self.is_terminal:
            if self.winner == 0:
                print("draw")
            elif self.winner == 1:
                print("team 1 victory")
            else:
                print("team 2 victory")

        print("-"*10)


class RandomnessHandler:
    # gutted out tree exploration options
    def __init__(self):
        pass
        # i removed all this when i took out tree exploration

    # gutted deterministic and explorable choices in favor of random
    def choose_random(self, choice: RandomChoice) -> Any:
        result = random.choices(choice.options, weights=choice.probabilities)[0]
        return result