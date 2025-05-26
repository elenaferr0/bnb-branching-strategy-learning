from pyscipopt import Model, Branchrule
from pyscipopt import SCIP_RESULT
import numpy as np
from collections import defaultdict
import pandas as pd
import math, json
import kagglehub, os

from problem import Problem, LEARNED_STRONG_BRANCHING, RELIABILITY_BRANCHING, PSEUDO_COST_BRANCHING, MOST_INFEASIBLE_BRANCHING, RANDOM_BRANCHING
from strong_branching import StrongBranchingRule

def benchmark_strategies(problems, branching_strategies, node_limits, time_limits_s):

def benchmark_predictors(problems, predictors, node_limits, time_limits_s):

def main():
    branching_strategies = [
        RELIABILITY_BRANCHING,
        MOST_INFEASIBLE_BRANCHING,
        PSEUDO_COST_BRANCHING,
        RANDOM_BRANCHING,
    ]

    time_limits = [0.5, 1, 2.5, 5, 30, 60, 5 * 60, 10 * 60]
    node_limits = [15, 30, 50, 100, 1000, 5000, 10000, 50000, 100000]

    s = stats()
    p = probs(s)
    benchmark_strategies(p.items(), branching_strategies, node_limits, time_limits)
    benchmark_predictors(p.items(), s.items(), node_limits, time_limits)

if __name__ == "__main__":
    # add a new predictor column to benchmark and set it to none
    stats()
    