
import pandas as pd
from collections import defaultdict

df = pd.read_csv('tr_clean.csv')
print(f"total rows: {len(df)}")
team_battles = defaultdict(list)

for idx, row in df.iterrows():
    team1_id = row['Team1_ID']
    team2_id = row['Team2_ID']
    team1_wins = row['Team1_Wins']
    team2_wins = row['Team2_Wins']
    draws = row['Draws']

    # track team1 battles
    team_battles[team1_id].append({
        'my_wins': team1_wins,
        'draws': draws
    })

    # track team2 battles
    team_battles[team2_id].append({
        'my_wins': team2_wins,
        'draws': draws
    })

# create output csv
results = []
for team_id in sorted(team_battles.keys()):
    battles = team_battles[team_id]

    # check if team was ever swept (0 wins AND 0 draws in any matchup)
    was_ever_swept = any(battle['my_wins'] == 0 and battle['draws'] == 0 for battle in battles)
    never_swept = not was_ever_swept

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
        'Never_Swept': never_swept
    })

# convert to pandas and sort
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('Never_Swept', ascending=False)

# save
results_df.to_csv('never_swept.csv', index=False)
