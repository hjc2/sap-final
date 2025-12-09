
# main file

import sys
from core import Team
from simulator import BattleSimulator
from pprint import pp
from team_combinations import generate_all_team_sequences, run_tournament

if __name__ == "__main__":
    # check for tournament mode
    if "--tournament" in sys.argv:
        print("Running FULL TOURNAMENT MODE")
        print("-"*10)

        teams = generate_all_team_sequences(team_length=3)

        output_file = run_tournament(teams, num_battles=1, chunk_size=10000)

        print("tournament complete")
        print(f"results saved to: {output_file}")

        

    if "--custom" in sys.argv:
        print("running in CUSTOM MODE") 

        teams = [Team().add_pets("Fish", "Ant", "Fish"),
        Team().add_pets("Ant", "Ant", "Fish"),
        Team().add_pets("Fish", "Fish", "Fish"),
        Team().add_pets("Fish", "Ant", "Cricket"),
        Team().add_pets("Fish", "Fish", "Beaver"),
        Team().add_pets("Ant", "Ant", "Otter"),
        Team().add_pets("Fish", "Ant", "Beaver"),
        Team().add_pets("Fish", "Ant", "Mosquito"),
        Team().add_pets("Fish", "Ant", "Ant"),
        Team().add_pets("Ant", "Fish", "Fish")]

        output_file = run_tournament(teams, num_battles=10000, chunk_size=10000)
        print("tournament complete")
        print(f"results saved to: {output_file}")

    else:
        # default.........
        print("example battle...")
        print("(use --tournament flag to run full tournament)\n")

        team1 = Team().add_pets("mosquito", "mosquito", "mosquito")
        team2 = Team().add_pets("pig", "pig", "pig", "pig", "pig")

        simulator = BattleSimulator()
        res = simulator.k_battles(team1, team2, num_simulations=10)
        pp(res)
        pp(simulator)