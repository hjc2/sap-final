
import pandas as pd
from collections import defaultdict

df = pd.read_csv('tr_clean.csv')
print(f"total rows: {len(df)}")
game = defaultdict(set)

for idx, row in df.iterrows():
    team1_id = row['Team1_ID']
    team2_id = row['Team2_ID']
    team1_wins = row['Team1_Wins']
    team2_wins = row['Team2_Wins']

    # add unique loss for team1
    if team2_wins > 0:
        game[team1_id].add(team2_id)

    # add unique loss for team2
    if team1_wins > 0:
        game[team2_id].add(team1_id)

    if (idx + 1) % 100000 == 0:
        print(f"Processed {idx + 1} rows...")

# create output csv
results = []
for team_id in sorted(game.keys()):
    loss_count = len(game[team_id])

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
        'Unique_Loss_Count': loss_count
    })

# convert to pandas and sort
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('Unique_Loss_Count', ascending=True)

# save
results_df.to_csv('unique_losses.csv', index=False)

