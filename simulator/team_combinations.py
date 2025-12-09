
from itertools import product
import csv
from datetime import datetime
from core import Team
from pets import list_available_pets
from simulator import BattleSimulator

def generate_all_team_sequences(team_length: int = 1) -> list[Team]:
    # team sequences
    available_pets = list_available_pets()
    all_sequences = list(product(available_pets, repeat=team_length))

    teams = []
    for sequence in all_sequences:
        team = Team()
        team.add_pets(*sequence)
        teams.append(team)

    return teams


def run_tournament(teams: list[Team], num_battles: int = 10, output_file: str = None, chunk_size: int = 1000) -> str:
    simulator = BattleSimulator()

    # generate output filename
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"tr_{timestamp}.csv"

    total_matchups = len(teams) * len(teams)  # full grid, not half
    matchup_count = 0

    print(f"\nStarting FULL GRID tournament with {len(teams)} teams...")
    print(f"total matchups: {total_matchups}")
    print(f"battles per matchup: {num_battles}")
    print(f"total simulations: {total_matchups * num_battles:,}")

    # open CSV file for streaming writes
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Team1_ID', 'Team1_Composition', 'Team2_ID', 'Team2_Composition', 'Team1_Wins', 'Team2_Wins', 'Draws', 'Total_Battles']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # full grid: each team plays every team (including itself)
        for i, team1 in enumerate(teams):
            print(f"Progress: {matchup_count}/{total_matchups:,} matchups ({100*matchup_count/total_matchups:.1f}%)")
            for j, team2 in enumerate(teams):
                matchup_count += 1

                # get team compositions as strings
                team1_comp = ", ".join([p.name for p in team1.get_alive_pets()])
                team2_comp = ", ".join([p.name for p in team2.get_alive_pets()])

                # run the battles
                battle_result = simulator.k_battles(team1, team2, num_simulations=num_battles)

                # write to csv
                writer.writerow({
                    'Team1_ID': i,
                    'Team1_Composition': team1_comp,
                    'Team2_ID': j,
                    'Team2_Composition': team2_comp,
                    'Team1_Wins': battle_result['team1_wins'],
                    'Team2_Wins': battle_result['team2_wins'],
                    'Draws': battle_result['draws'],
                    'Total_Battles': num_battles
                })

                # flush
                if matchup_count % chunk_size == 0:
                    csvfile.flush()
                    print(f"flushed count: {matchup_count:,}/{total_matchups:,})")
    print(f"processed {matchup_count:,} matchups")
    print(f"results saved to: {output_file}")


    return output_file