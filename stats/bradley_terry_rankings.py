
import pandas as pd
import numpy as np

df = pd.read_csv('tr_clean.csv')
print(f"total rows: {len(df)}")

# build win/loss matrices
num_teams = df['Team1_ID'].max() + 1
wins = np.zeros((num_teams, num_teams))
comparisons = np.zeros((num_teams, num_teams))

for idx, row in df.iterrows():
    i = int(row['Team1_ID'])
    j = int(row['Team2_ID'])
    team1_wins = row['Team1_Wins']
    team2_wins = row['Team2_Wins']
    draws = row['Draws']

    # count draws as 0.5 wins for each team
    wins[i, j] = team1_wins + (0.5 * draws)
    wins[j, i] = team2_wins + (0.5 * draws)

    # total comparisons
    total = team1_wins + team2_wins + draws
    comparisons[i, j] = total
    comparisons[j, i] = total

# bradley-terry iterative algorithm
strengths = np.ones(num_teams)
max_iterations = 1000
tolerance = 1e-6

for iteration in range(max_iterations):
    old_strengths = strengths.copy()

    # update each team's strength
    for i in range(num_teams):
        total_wins_i = np.sum(wins[i, :])
        denominator = 0.0
        for j in range(num_teams):
            if i != j and comparisons[i, j] > 0:
                denominator += comparisons[i, j] / (old_strengths[i] + old_strengths[j])

        if denominator > 0:
            strengths[i] = total_wins_i / denominator

    # normalize to prevent overflow
    strengths = strengths / np.exp(np.mean(np.log(strengths + 1e-10)))

    # check convergence
    max_change = np.max(np.abs(strengths - old_strengths))
    if max_change < tolerance:
        break

# create output csv
results = []
for team_id in range(num_teams):
    # get team comp
    team_comp = df[df['Team1_ID'] == team_id]['Team1_Composition'].iloc[0]

    # calculate win statistics
    total_wins = np.sum(wins[team_id, :])
    total_games = np.sum(comparisons[team_id, :])
    win_rate = total_wins / total_games if total_games > 0 else 0

    # append
    results.append({
        'Team_ID': team_id,
        'Team_Composition': team_comp,
        'BT_Strength': strengths[team_id],
        'Total_Wins': total_wins,
        'Total_Games': total_games,
        'Win_Rate': win_rate
    })

# convert to pandas and sort
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('BT_Strength', ascending=False)
results_df['Rank'] = range(1, len(results_df) + 1)

# save
results_df.to_csv('bradley_terry_rankings.csv', index=False)
