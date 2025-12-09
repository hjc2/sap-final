
### Simulation Code

Code for simulating the battles and assembling the wins database

### Stats Scripts

Analysis scripts for tournament results in `stats/`:

- [**bradley_terry_rankings.py**](stats/bradley_terry_rankings.py) - Ranks teams using Bradley-Terry model based on head-to-head results
- [**total_win_count.py**](stats/total_win_count.py) - Counts total wins per team across all matchups
- [**total_loss_count.py**](stats/total_loss_count.py) - Counts total losses per team across all matchups
- [**unique_losses.py**](stats/unique_losses.py) - Finds how many unique opponents each team lost to
- [**always_onewin.py**](stats/always_onewin.py) - Identifies teams that win at least once in every matchup
- [**never_swept.py**](stats/never_swept.py) - Identifies teams that never get completely swept (0-0 record)
- [**unbeaten_teams.py**](stats/never_swept.py) - Identifies teams that are never beaten

These are run on the [**tr_clean.csv**](stats/tr_clean.csv) 1000 battles dataset with the output dataset in [**data**](stats/data)

### Tools Scripts

Analysis tools for tournament results in `tools/`:

- [**heatmap.py**](tools/heatmap.py) - displays head to head results in a heatmap (2 points for a win, 1 for twin, 0 for a loss)
- [**remove_team_numbers.py**](tools/remove_team_numbers.py) - Filters out the numberical identifiers from the tournament results

### NE

- [**nash_equilibrium_fast.py**](ne/nash_equilibrium_fast.py) - solves for the NE using scipy
