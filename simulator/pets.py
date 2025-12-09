
from core import Pet, TriggerType
from abilities import (
    mosquito_ability,
    cricket_ability,
    horse_ability,
    ant_ability
)

### Pets

def create_ant() -> Pet:
    """ant: faint -> give a friend (+1,+1)"""
    pet = Pet(
        name="Ant",
        attack=2,
        health=2,
        level=1
    )
    pet.trigger_type = TriggerType.FAINT
    pet.ability = ant_ability
    return pet

def create_beaver() -> Pet:
    """beaver: shop ability"""
    pet = Pet(
        name="Beaver",
        attack=3,
        health=2,
        level=1
    )
    return pet

def create_cricket() -> Pet:
    """cricket: faint -> summon 1/1 zombie cricket"""
    pet = Pet(
        name="Cricket",
        attack=1,
        health=2,
        level=1
    )
    pet.trigger_type = TriggerType.FAINT
    pet.ability = cricket_ability
    return pet

def create_duck() -> Pet:
    """duck: shop ability"""
    return Pet(
        name="Duck",
        attack=2,
        health=3,
        level=1
    )

def create_fish() -> Pet:
    """fish: basic pet with no ability"""
    return Pet(
        name="Fish",
        attack=2,
        health=3,
        level=1
    )

def create_horse() -> Pet:
    """horse: friend summoned -> give it +1/+1"""
    pet = Pet(
        name="Horse",
        attack=2,
        health=1,
        level=1
    )
    pet.trigger_type = TriggerType.FRIEND_SUMMONED
    pet.ability = horse_ability
    return pet

def create_mosquito() -> Pet:
    """mosquito: start of battle -> deal 1 damage to random enemy"""
    pet = Pet(
        name="Mosquito",
        attack=2,
        health=2,
        level=1
    )
    pet.trigger_type = TriggerType.START_OF_BATTLE
    pet.ability = mosquito_ability
    return pet

def create_mouse() -> Pet:
    """mouse: shop ability"""
    return Pet(
        name="Mouse",
        attack=1,
        health=2,
        level=1
    )

def create_otter() -> Pet:
    """otter: shop ability"""
    return Pet(
        name="Otter",
        attack=1,
        health=3,
        level=1
    )

def create_pig() -> Pet:
    """pig: shop ability"""
    return Pet(
        name="Pig",
        attack=4,
        health=1,
        level=1
    )

#### Pet registry

PET_REGISTRY = {
    "ant": create_ant,
    "beaver": create_beaver,
    "cricket": create_cricket,
    # "duck": create_duck,
    "fish": create_fish,
    "horse": create_horse,
    "mosquito": create_mosquito,
    "mouse": create_mouse,
    "otter": create_otter,
    "pig":create_pig
}


def create_pet(pet_name: str) -> Pet:

    name_lower = pet_name.lower()
    if name_lower not in PET_REGISTRY:
        available = ", ".join(PET_REGISTRY.keys())
        raise ValueError(f"Unknown pet '{pet_name}'. Available: {available}")

    return PET_REGISTRY[name_lower]()

# returns the registry str
def list_available_pets() -> list[str]:
    # return list
    return list(PET_REGISTRY.keys())

# mod a pet at index i
def modify_pet_at_index(team, index: int, **modifications) -> bool:
    # get the pet at the specified index
    pet = team.get_pet_at(index)

    if pet is None:
        return False

    # apply all modifications
    for attribute, value in modifications.items():
        if hasattr(pet, attribute):
            setattr(pet, attribute, value)
        else:
            raise AttributeError(f"Pet has no attribute '{attribute}'")

    return True