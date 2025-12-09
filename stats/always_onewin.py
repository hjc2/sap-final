
import pandas as pd
from collections import defaultdict

df = pd.read_csv('tr_clean.csv')
print(f"total rows: {len(df)}")

# track battles for each team
team_battles = defaultdict(list)

for idx, row in df.iterrows():
    team1_id = row['Team1_ID']
    team2_id = row['Team2_ID']
    team1_wins = row['Team1_Wins']
    team2_wins = row['Team2_Wins']

    # for team1 in this matchup
    team_battles[team1_id].append({
        'opponent_id': team2_id,
        'my_wins': team1_wins,
        'opponent_wins': team2_wins
    })

    # for team2 in this matchup
    team_battles[team2_id].append({
        'opponent_id': team1_id,
        'my_wins': team2_wins,
        'opponent_wins': team1_wins
    })

# find teams that get at least 1 win in every matchup
teams_data = {}
for team_id, battles in team_battles.items():
    # check if this team has at least 1 win in every battle
    has_win_in_all_battles = all(battle['my_wins'] > 0 for battle in battles)

    teams_data[team_id] = {
        'always_wins': has_win_in_all_battles,
        'total_matchups': len(battles)
    }

# create output csv
results = []
for team_id in sorted(teams_data.keys()):
    team_info = teams_data[team_id]

    # get team comp from [0]
    team_row = df[(df['Team1_ID'] == team_id) | (df['Team2_ID'] == team_id)].iloc[0]
    if team_row['Team1_ID'] == team_id:
        composition = team_row['Team1_Composition']
    else:
        composition = team_row['Team2_Composition']

    # append
    results.append({
        'Team_ID': team_id,
        'Team_Composition': composition,
        'Always_Wins_Once': 1 if team_info['always_wins'] else 0,
        'Total_Matchups': team_info['total_matchups']
    })

# convert to pandas and sort
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('Always_Wins_Once', ascending=False)

# save
results_df.to_csv('always_onewin.csv', index=False)
