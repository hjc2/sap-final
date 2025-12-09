
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('tr_clean.csv')
print(f"total rows: {len(df)}")

# get number of teams and battles
num_teams = df['Team1_ID'].max() + 1
total_battles = df['Total_Battles'].iloc[0]

print(f"teams: {num_teams}")
print(f"battles per matchup: {total_battles}")

# create points matrix
points_matrix = np.zeros((num_teams, num_teams))

# calculate points for each matchup
for idx, row in df.iterrows():
    team1_id = int(row['Team1_ID'])
    team2_id = int(row['Team2_ID'])

    # team1 points: 2 per win, 1 per draw
    team1_points = (row['Team1_Wins'] * 2) + (row['Draws'] * 1)
    points_matrix[team1_id, team2_id] = team1_points

# calculate total points for each team
team_total_points = points_matrix.sum(axis=1)

# create heatmap
fig_size = max(14, num_teams / 50)
fig = plt.figure(figsize=(fig_size, fig_size), facecolor='white')

# max possible points per matchup
max_points = total_battles * 2

# custom colormap
from matplotlib.colors import LinearSegmentedColormap
colors = ['#FF1493', '#FFD700', '#90EE90', '#006400']
cmap = LinearSegmentedColormap.from_list('points', colors, N=256)

# create heatmap
ax = plt.gca()
ax.set_facecolor('white')

sns.heatmap(
    points_matrix,
    vmin=0,
    vmax=max_points,
    cmap=cmap,
    square=True,
    cbar_kws={'label': 'Team 1 Points (Wins=2, Draws=1, Losses=0)', 'shrink': 0.8},
    xticklabels=False,
    yticklabels=False,
    ax=ax
)

plt.title(f'Tournament Heatmap: Team Performance\n{num_teams} Teams × {total_battles} Battles per Matchup', fontsize=14, pad=20)
plt.xlabel('Opponent Team ID', fontsize=12)
plt.ylabel('Team ID', fontsize=12)

grid_interval = 100

ax.set_xticks(np.arange(0, num_teams, grid_interval))
ax.set_yticks(np.arange(0, num_teams, grid_interval))
ax.set_xticklabels([str(i) for i in range(0, num_teams, grid_interval)])
ax.set_yticklabels([str(i) for i in range(0, num_teams, grid_interval)])

plt.tight_layout()

# save heatmap
output_image = 'tr_clean_heatmap_unsorted.png'
plt.savefig(output_image, dpi=200, bbox_inches='tight')
