from pyscipopt import Model, Branchrule
from pyscipopt import SCIP_RESULT
import numpy as np
from collections import defaultdict
import pandas as pd
import math, json
import kagglehub, os

from problem import Problem, LEARNED_STRONG_BRANCHING, RELIABILITY_BRANCHING, PSEUDO_COST_BRANCHING, MOST_INFEASIBLE_BRANCHING, RANDOM_BRANCHING
from strong_branching import StrongBranchingRule


class LearnedStrongBranching(StrongBranchingRule):
    def __init__(self, model, predictor, A, b, c, logged, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model: Model = model
        self.predictor = predictor
        self.A = A
        self.b = b
        self.c = c
        self.logged = logged
        self.n_branches_by_var = defaultdict(int)
        self.objective_increases_by_var = defaultdict(list)

    def branchexeclp(self, allowaddcons):
        branch_cands, branch_cand_sols, branch_cand_fracs, ncands, npriocands, nimplcands = self.model.getLPBranchCands()

        best_cand_idx = 0
        best_cand_score = float('-inf')

        for i in range(npriocands):
            self.n_branches_by_var[branch_cands[i].name] += 1
            score = self.predict_score(branch_cand_fracs[i], branch_cands[i])
            if score > best_cand_score:
                best_cand_score = score
                best_cand_idx = i

        self.model.branchVarVal(branch_cands[best_cand_idx], branch_cand_sols[best_cand_idx])
        return {"result": SCIP_RESULT.BRANCHED}

    def predict_score(self, frac, var):
        features = self.extract_feats(frac, var)
        features = pd.DataFrame([features])
        return self.predictor.predict(pd.DataFrame(features))

def stats():
    stats_path = kagglehub.dataset_download("elenaferr0/strongbranchingstats")
    stats_path = f"{stats_path}/Stats"
    test_files = [f for f in os.listdir(stats_path) if 'test' in f]
    stats_dfs = {
        f.replace("_test_stats.csv", ""): pd.read_csv(f"{stats_path}/{f}") for f in test_files
    }
    for f, stats_df in stats_dfs.items():
        print(f"Stats for {f}:")
        print(f"Number of problems: {len(stats_df)}")
        print(f"Average number of variables: {stats_df['n_vars'].mean()}")
        print(f"Average number of constraints: {stats_df['n_constraints'].mean()}")
        print(f"Average sb decision: {stats_df['sb_decision'].mean()}")
        print(f"Average time: {stats_df['time'].mean()} seconds")
        print()

    return {
        f: df['name'].values
        for f, df in stats_dfs.items()
    }

def probs(stats):
    probs_path = kagglehub.dataset_download("elenaferr0/lp-probs")
    probs_path = f"{probs_path}/LP-Probs"
    # print(probs_path)
    # print(os.listdir(probs_path))

    problems = {}
    for category, names in stats.items():
        problems[category] = []
        for name in names:
            file_path = f"{probs_path}/{category}/{name}.lp"
            if os.path.exists(file_path):
                # prob = Problem.from_model(file_path)
                # prob.name = name
                problems[category].append((file_path, name))
            else:
                print(f"Problem {name} not found in {file_path}")
    return problems

def benchmark(problems, branching_strategies, node_limits, time_limits_s):
    # solved_optimally_cache = {} #(problem name,strategy): True
    if os.path.exists("benchmark_results.csv"):
        benchmark_df = pd.read_csv("benchmark_results.csv")
        print(f"Loaded existing benchmark results with {len(benchmark_df)} rows.")
    else:
        benchmark_df = pd.DataFrame(columns=['name', 'strategy', 'time_limit', 'node_limit', 'status', 'gap', 'n_vars', 'n_constraints', 'sb_decision'])

    # create a cache (name, strategy) -> True if problem was solved optimally with that strategy
    solved_optimally_cache = defaultdict(bool)
    for index, row in benchmark_df.iterrows():
        key = (row['name'], row['strategy'])
        if row['status'] == 'optimal':
            solved_optimally_cache[key] = True
        else:
            solved_optimally_cache[key] = False

    for category, probs in problems:
        for filepath, name in probs:
            prob = Problem.from_model(filepath, name)
            for strategy in branching_strategies:
                achieved_optimality = False
                for time_limit in time_limits_s:
                    for node_limit in node_limits:
                        # Check if row already exists
                        if benchmark_df[(benchmark_df['name'] == prob.name) & (benchmark_df['strategy'] == strategy) & (
                                benchmark_df['time_limit'] == time_limit) & (benchmark_df['node_limit'] == node_limit)].shape[0] > 0:
                            print(f"Row already exists for {prob.name} with strategy {strategy}, time limit {time_limit}, and node limit {node_limit}. Skipping.")
                            continue

                        if solved_optimally_cache.get((prob.name, strategy), False):
                            print(f"Problem {prob.name} already solved optimally with strategy {strategy}. Skipping.")
                            continue

                        print(f"Solving {prob.name} with strategy {strategy}, time limit {time_limit}, and node limit {node_limit}")
                        row = prob.solve_with_rule(strategy, logged=True, max_nodes=node_limit, timelimit=time_limit)
                        row['strategy'] = strategy
                        row['time_limit'] = time_limit
                        row['node_limit'] = node_limit
                        pdata = pd.DataFrame.from_dict(row, orient='index').T
                        benchmark_df = pd.concat([benchmark_df, pdata], ignore_index=True)
                        benchmark_df.to_csv(f"benchmark_results.csv", index=False)

                        if row['status'] == 'optimal':
                            solved_optimally_cache[(category, strategy)] = True
                            achieved_optimality = True
                            break # exit node_limits loop
                    if achieved_optimality:
                        break # exit time_limits loop
            prob.model.freeProb()
    # display(benchmark_df)

def main():
    branching_strategies = [
        # LEARNED_STRONG_BRANCHING,
        RELIABILITY_BRANCHING,
        MOST_INFEASIBLE_BRANCHING,
        PSEUDO_COST_BRANCHING,
        RANDOM_BRANCHING,
    ]

    # time_limits_s = [5, 60, 5 * 60, 10 * 60]
    # node_limits = [50, 100, 1000, 5000, 10000]
    time_limits_s = [0.5, 1, 2.5, 5, 30, 60]
    node_limits = [15, 30, 50, 100, 1000, 5000, 10000]

    s = stats()
    p = probs(s)
    benchmark(p.items(), branching_strategies, node_limits, time_limits_s)

if __name__ == "__main__":
    main()