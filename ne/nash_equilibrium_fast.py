
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from typing import Tuple, List, Dict
import warnings
import os
warnings.filterwarnings('ignore')


class FastNashSolver:

    def __init__(self, csv_path: str):
        print(f"loading data from {csv_path}")

        # get teams
        first_chunk = pd.read_csv(csv_path, nrows=1000)
        self.n_teams = max(first_chunk['Team1_ID'].max(), first_chunk['Team2_ID'].max()) + 1
        print(f"found {self.n_teams} teams")

        # create team lookup
        self.team_names = {}
        for _, row in first_chunk.iterrows():
            self.team_names[row['Team1_ID']] = row['Team1_Composition']
            self.team_names[row['Team2_ID']] = row['Team2_Composition']

        # build payoff matrix
        print("building payoff matrix")
        self.payoff_matrix = np.zeros((self.n_teams, self.n_teams), dtype=np.float32)

        chunk_size = 50000
        for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size)):
            for _, row in chunk.iterrows():
                t1 = row['Team1_ID']
                t2 = row['Team2_ID']
                total = row['Total_Battles']

                if total > 0:
                    payoff = (row['Team1_Wins'] - row['Team2_Wins']) / total
                    self.payoff_matrix[t1, t2] = payoff
                    self.payoff_matrix[t2, t1] = -payoff

                # update team names
                if t1 not in self.team_names:
                    self.team_names[t1] = row['Team1_Composition']
                if t2 not in self.team_names:
                    self.team_names[t2] = row['Team2_Composition']

            print(f"processed chunk {i+1}")

        print(f"payoff matrix: {self.payoff_matrix.shape}")

    def find_simple_cycles(self) -> List[Dict]:
        print("searching for cycles")

        cycles = []
        threshold = 0.15

        # sample teams
        sample_size = min(200, self.n_teams)
        sample_teams = np.random.choice(self.n_teams, sample_size, replace=False)

        for i in sample_teams:
            # teams that i beats
            beats_i = np.where(self.payoff_matrix[i] > threshold)[0]

            for j in beats_i:
                # teams that j beats
                beats_j = np.where(self.payoff_matrix[j] > threshold)[0]

                for k in beats_j:
                    # check if k beats i
                    if self.payoff_matrix[k, i] > threshold:
                        cycles.append({
                            'team_ids': [i, j, k],
                            'teams': [self.team_names[i], self.team_names[j], self.team_names[k]],
                            'payoffs': [
                                self.payoff_matrix[i, j],
                                self.payoff_matrix[j, k],
                                self.payoff_matrix[k, i]
                            ],
                            'avg_dominance': (self.payoff_matrix[i, j] +
                                            self.payoff_matrix[j, k] +
                                            self.payoff_matrix[k, i]) / 3
                        })

        # remove duplicates
        unique_cycles = []
        seen = set()
        for cycle in cycles:
            cycle_set = frozenset(cycle['team_ids'])
            if cycle_set not in seen:
                seen.add(cycle_set)
                unique_cycles.append(cycle)

        print(f"found {len(unique_cycles)} cycles")

        # print top cycles
        if unique_cycles:
            sorted_cycles = sorted(unique_cycles, key=lambda x: x['avg_dominance'], reverse=True)
            for i, cycle in enumerate(sorted_cycles[:5]):
                print(f"cycle {i+1}: {cycle['avg_dominance']:.3f}")
                for j in range(3):
                    print(f"  {cycle['teams'][j]} beats {cycle['teams'][(j+1)%3]} ({cycle['payoffs'][j]:+.3f})")

        return unique_cycles

    def solve_nash_equilibrium(self) -> Tuple[np.ndarray, float]:
        print("solving nash equilibrium")
        print(f"problem size: {self.n_teams} teams")

        # variables
        c = np.zeros(self.n_teams + 1, dtype=np.float32)
        c[-1] = -1

        # constraints
        A_ub = np.column_stack([-self.payoff_matrix.T, np.ones(self.n_teams, dtype=np.float32)])
        b_ub = np.zeros(self.n_teams, dtype=np.float32)

        # zerp sum game
        A_eq = np.zeros((1, self.n_teams + 1), dtype=np.float32)
        A_eq[0, :-1] = 1
        b_eq = np.array([1], dtype=np.float32)

        # bounds
        bounds = [(0, None) for _ in range(self.n_teams)] + [(None, None)]

        print("running LP solver")
        result = linprog(
            c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
            bounds=bounds, method='highs', options={'disp': False}
        )

        if not result.success:
            print(f"LP solver failed: {result.message}")
            return None, None

        strategy = result.x[:-1]
        value = result.x[-1]

        support_size = np.sum(strategy > 1e-6)
        print(f"game value: {value:.6f}")
        print(f"support size: {support_size} teams ({100*support_size/self.n_teams:.1f}%)")

        return strategy, value

    def analyze_results(self, strategy: np.ndarray, value: float):
        print("analyzing results")

        threshold = 1e-6
        support_indices = np.where(strategy > threshold)[0]

        # build support dataframe
        support_data = []
        for idx in support_indices:
            expected_payoff = self.payoff_matrix[idx] @ strategy
            support_data.append({
                'Team_ID': idx,
                'Composition': self.team_names[idx],
                'Probability': strategy[idx],
                'Expected_Payoff': expected_payoff
            })

        support_df = pd.DataFrame(support_data)
        support_df = support_df.sort_values('Probability', ascending=False)

        print(f"\ntop 20 teams in nash equilibrium:")
        for i, row in support_df.head(20).iterrows():
            print(f"{row['Probability']:.6f} - {row['Composition']}")

        # dominant teams vs uniform
        print(f"\ntop 20 dominant teams (vs uniform random):")
        uniform = np.ones(self.n_teams) / self.n_teams
        payoffs_vs_uniform = self.payoff_matrix @ uniform

        top_indices = np.argsort(payoffs_vs_uniform)[-20:][::-1]

        for idx in top_indices:
            payoff = payoffs_vs_uniform[idx]
            win_rate = (payoff + 1) / 2
            print(f"{win_rate:.1%} - {self.team_names[idx]}")

        # exploitability
        expected_payoffs_vs_eq = self.payoff_matrix @ strategy
        nash_value = strategy @ expected_payoffs_vs_eq
        best_response_payoff = np.max(expected_payoffs_vs_eq)
        best_response_idx = np.argmax(expected_payoffs_vs_eq)

        exploitability = best_response_payoff - nash_value

        print(f"\nnash equilibrium value: {nash_value:.6f}")
        print(f"best response payoff: {best_response_payoff:.6f}")
        print(f"exploitability: {exploitability:.6f}")
        print(f"best response team: {self.team_names[best_response_idx]}")

        # save results
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_base = os.path.join(script_dir, 'nash_results')

        support_df.to_csv(f'{output_base}_support.csv', index=False)
        print(f"\nsaved support teams to {output_base}_support.csv")

        dominant_data = []
        for idx in top_indices:
            payoff = payoffs_vs_uniform[idx]
            dominant_data.append({
                'Team_ID': idx,
                'Composition': self.team_names[idx],
                'Avg_Payoff_vs_Uniform': payoff,
                'Win_Rate_vs_Uniform': (payoff + 1) / 2
            })
        dominant_df = pd.DataFrame(dominant_data)
        dominant_df.to_csv(f'{output_base}_dominant.csv', index=False)
        print(f"saved dominant teams to {output_base}_dominant.csv")

def main():
    import sys

    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'tr_100clean.csv')

    if len(sys.argv) > 1:
        csv_path = sys.argv[1]

    solver = FastNashSolver(csv_path)
    cycles = solver.find_simple_cycles()
    strategy, value = solver.solve_nash_equilibrium()

    if strategy is not None:
        solver.analyze_results(strategy, value)


if __name__ == '__main__':
    main()
