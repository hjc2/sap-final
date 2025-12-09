
from core import Team
from simulator import BattleSimulator

### github testing of sim

def atol(actual, expected, tol):
    assert abs(actual - expected) <= tol

# should be a draw
def test_horse():
    # horse buffs summoned crickets
    team1 = Team().add_pets("cricket", "cricket", "horse")
    team2 = Team().add_pets("pig", "mouse", "pig", "mouse", "mouse")

    simulator = BattleSimulator(deterministic=True)

    assert(simulator.simulate_battle(team1, team2).winner == 0)

# ant win
def test_ant():
    # ant buffs other ant, so it survives fish attack
    team1 = Team().add_pets("ant", "ant")
    team2 = Team().add_pets("fish")

    simulator = BattleSimulator(deterministic=True)

    assert(simulator.simulate_battle(team1, team2).winner == 1)

def test_mosquito():
    # mosquito shoots one, kills the other, ties
    team1 = Team().add_pets("pig", "pig")
    team2 = Team().add_pets("mosquito")

    simulator = BattleSimulator(deterministic=True)

    assert(simulator.simulate_battle(team1, team2).winner == 0)

def test_three_five():
    # mosquitos kill between 1 and 3 pigs
    team1 = Team().add_pets("mosquito", "mosquito", "mosquito")
    team2 = Team().add_pets("pig", "pig", "pig", "pig", "pig")

    simulator = BattleSimulator()
    res = simulator.k_battles(team1, team2, num_simulations=1000)
    
    # 4/5 * 3/5
    atol(res['team1_win_rate'], 48, 5)
    # 1/5 * 1/5
    atol(res['team2_win_rate'], 4, 3)
    atol(res['draw_rate'], 48, 5)