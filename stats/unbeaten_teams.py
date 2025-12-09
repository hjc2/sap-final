
import pandas as pd
from collections import defaultdict

df = pd.read_csv('../stats/tr_clean.csv')
print(f"total rows: {len(df)}")
team_losses = defaultdict(int)

for idx, row in df.iterrows():
    team1_id = row['Team1_ID']
    team2_id = row['Team2_ID']
    team1_wins = row['Team1_Wins']
    team2_wins = row['Team2_Wins']

    # track losses
    team_losses[team1_id] += team2_wins
    team_losses[team2_id] += team1_wins

# find unbeaten
unbeaten_teams = []
for team_id in sorted(team_losses.keys()):
    loss_count = team_losses[team_id]

    if loss_count == 0:
        # get team composition
        team_row = df[(df['Team1_ID'] == team_id) | (df['Team2_ID'] == team_id)].iloc[0]
        if team_row['Team1_ID'] == team_id:
            composition = team_row['Team1_Composition']
        else:
            composition = team_row['Team2_Composition']

        unbeaten_teams.append({
            'Team_ID': team_id,
            'Team_Composition': composition
        })

# print results
if unbeaten_teams:
    print("Unbeaten Teams:")
    for team in unbeaten_teams:
        print(f"  Team {team['Team_ID']}: {team['Team_Composition']}")
else:
    print("no unbeaten teams")
