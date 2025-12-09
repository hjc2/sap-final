
import pandas as pd
from collections import defaultdict

df = pd.read_csv('tr_clean.csv')
print(f"total rows: {len(df)}")
game = defaultdict(int)

for idx, row in df.iterrows():
    team1_id = row['Team1_ID']
    team2_id = row['Team2_ID']
    team1_wins = row['Team1_Wins']
    team2_wins = row['Team2_Wins']

    # add team1 losses
    game[team1_id] += team2_wins

    # add team2 losses
    game[team2_id] += team1_wins

# create output csv
results = []
for team_id in sorted(game.keys()):
    loss_count = game[team_id]

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
        'Total_Loss_Count': loss_count
    })

# convert to pandas and sort
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('Total_Loss_Count', ascending=True)

# save
results_df.to_csv('total_loss_count.csv', index=False)