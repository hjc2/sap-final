
import random

from core import GameState, Pet, Team

# implementations of the pets abilities

def _trigger_friend_summoned(state: GameState, own_team: Team, summoned_pet: Pet):
    from core import TriggerType
    for pet in own_team.get_alive_pets():
        if pet is not summoned_pet and pet.trigger_type == TriggerType.FRIEND_SUMMONED and pet.ability:
            pet.ability(state, pet, own_team, summoned_pet=summoned_pet)

def ant_ability(state: GameState, self_pet: Pet, own_team: Team):
    alive_friends = [p for p in own_team.get_alive_pets() if p is not self_pet]
    if alive_friends:
        target = random.choice(alive_friends)
        target.attack += 1
        target.health += 1

def cricket_ability(state: GameState, self_pet: Pet, own_team: Team):
    from core import Pet, TriggerType
    zombie = Pet(name="Zombie Cricket", attack=1, health=1)
    if self_pet.position is not None:
        own_team.remove_pet(self_pet)
    success = own_team.add_pet(zombie)
    if success:
        _trigger_friend_summoned(state, own_team, zombie)

def mosquito_ability(state: GameState, self_pet: Pet, own_team: Team):
    enemy_team = state.team2 if own_team is state.team1 else state.team1
    alive_enemies = enemy_team.get_alive_pets()
    if not alive_enemies:
        return
    target = random.choice(alive_enemies)
    target.take_damage(1)

def horse_ability(state: GameState, self_pet: Pet, own_team: Team, summoned_pet: Pet = None):
    if summoned_pet is None:
        return
    summoned_pet.attack += 1