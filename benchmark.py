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
    stats = dict(map(lambda x: (x.replace("_test_stats.csv", ""), pd.read_csv(f"{stats_path}/{x}")['name'].values), test_files))
    # TODO: print some average stats for each dataframe
    print(stats)
    return stats

def probs(stats):
    probs_path = kagglehub.dataset_download("elenaferr0/lp-probs")
    probs_path = f"{probs_path}/LP-Probs"
    print(probs_path)
    print(os.listdir(probs_path))

    problems = {}
    for category, names in stats.items():
        problems[category] = []
        for name in names:
            file_path = f"{probs_path}/{category}/{name}.lp"
            if os.path.exists(file_path):
                prob = Problem.from_model(file_path)
                problems[category].append(prob)
            else:
                print(f"Problem {name} not found in {file_path}")
    return problems

def save_tuple_dict_to_csv(dictionary, filepath):
    # Create lists for each column
    key1_list = []
    key2_list = []
    value_list = []
    
    # Split tuple keys into separate columns
    for (k1, k2), value in dictionary.items():
        key1_list.append(k1)
        key2_list.append(k2)
        value_list.append(value)
    
    # Create DataFrame
    df = pd.DataFrame({
        'key1': key1_list,
        'key2': key2_list,
        'value': value_list
    })
    
    # Save to CSV
    df.to_csv(filepath, index=False)

def load_tuple_dict_from_csv(filepath):
    # Read CSV
    df = pd.read_csv(filepath)
    
    # Convert back to dictionary with tuple keys
    result_dict = {
        (row['key1'], row['key2']): row['value'] 
        for _, row in df.iterrows()
    }
    
    return result_dict

def benchmark(problems, branching_strategies, node_limits, time_limits_s):
    # solved_optimally_cache = {} #(problem name,strategy): True
    if os.path.exists("benchmark_results.csv"):
        benchmark_df = pd.read_csv("benchmark_results.csv")
        print(f"Loaded existing benchmark results with {len(benchmark_df)} rows.")
    else:
        benchmark_df = pd.DataFrame(columns=['name', 'strategy', 'time_limit', 'node_limit', 'status', 'gap', 'n_vars', 'n_constraints', 'sb_decision'])
    solved_optimally_cache = load_tuple_dict_from_csv("solved_optimally.json") if os.path.exists("solved_optimally.json") else {}

    for name, probs in problems:
        for prob in probs:
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
                        row = prob.solve_with_rule(strategy, logged=False, max_nodes=node_limit, timelimit=time_limit)
                        row['strategy'] = strategy
                        row['time_limit'] = time_limit
                        row['node_limit'] = node_limit
                        pdata = pd.DataFrame.from_dict(row, orient='index').T
                        benchmark_df = pd.concat([benchmark_df, pdata], ignore_index=True)
                        benchmark_df.to_csv(f"benchmark_results.csv", index=False)

                        if row['status'] == 'optimal':
                            solved_optimally_cache[(name, strategy)] = True
                            save_tuple_dict_to_csv(solved_optimally_cache, "solved_optimally.csv")
                            achieved_optimality = True
                            break # exit node_limits loop
                    if achieved_optimality:
                        break # exit time_limits loop
    # display(benchmark_df)

def main():
    branching_strategies = [
        # LEARNED_STRONG_BRANCHING,
        RELIABILITY_BRANCHING,
        MOST_INFEASIBLE_BRANCHING,
        PSEUDO_COST_BRANCHING,
        RANDOM_BRANCHING,
    ]

    time_limits_s = [5, 60, 5 * 60, 10 * 60]
    node_limits = [50, 100, 1000, 5000, 10000]
    
    s = stats()
    p = probs(s)
    benchmark(p.items(), branching_strategies, node_limits, time_limits_s)

if __name__ == "__main__":
    main()