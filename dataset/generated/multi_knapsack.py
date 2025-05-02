import random
import numpy as np

"""
Formulation
max sum_i^n sum_{j in N_i} p_ij * x_ij
s.t.
    sum_i^k sum_{j in N_i} w_ij * x_ij <= W_j
    sum_{j in N_i} x_ij = 1 forall i
    x_ij in {0, 1} forall j in N_i, forall i
"""

def multi_knapsack(n_problems: int, max_items: int, max_knapsacks: int, max_knapsack_capacity: float, max_item_profit: float, max_item_weight: float):
    return [__generate_problem(i, max_items, max_knapsacks, max_knapsack_capacity, max_item_profit, max_item_weight) for i in range(n_problems)]

def __generate_problem(id: int, max_items: int, max_knapsacks: int, max_knapsack_capacity: float, max_item_profit: float, max_item_weight: float):
    n_knapsacks = random.randint(1, max_knapsacks)
    n_items = random.randint(1, max_items)
    knapsack_capacities = np.random.uniform(1, max_knapsack_capacity, n_knapsacks)
    item_profits = np.random.uniform(1, max_item_profit, n_items)
    item_weights = np.random.uniform(1, max_item_weight, n_items)

    n_vars = n_items * n_knapsacks # x_ij
    c = -np.tile(item_profits, n_knapsacks) # convert to minimiz. problem

    A, b, types = [], [], []

    ## constraints
    # sum_i^k sum_{j in N_i} w_ij * x_ij <= W_j
    for j in range(n_knapsacks):
        row = np.zeros(n_vars)
        for i in range(n_items):
            row[i * n_knapsacks + j] = item_weights[i]
        A.append(row)
        b.append(knapsack_capacities[j])
        types.append('L')

    # sum_{j in N_i} x_ij <= 1 forall i
    for i in range(n_items):
        row = np.zeros(n_vars)
        for j in range(n_knapsacks):
            row[i * n_knapsacks + j] = 1
        A.append(row)
        b.append(1)
        types.append('E')

    A = np.array(A)
    b = np.array(b)
    types = np.array(types)
    bnd = [{"LO": 0, "UP": 1} for _ in range(n_vars)]

    return f"random_MKP_{id}", types, c, A, b, bnd
