import numpy as np

from dataset.solver.problem import Problem

"""
Formulation
max sum_i^n sum_{j in N_i} p_ij * x_ij
s.t.
    sum_i^k sum_{j in N_i} w_ij * x_ij <= W_j
    sum_{j in N_i} x_ij = 1 forall i
    x_ij in {0, 1} forall j in N_i, forall i
"""


def multi_knapsack(n_problems: int, items: (int, int), knapsacks: (int, int), knapsack_capacity: (float, float),
                   item_profit: (float, float), item_weight: (float, float)):
    return [__generate_problem(i, items, knapsacks, knapsack_capacity, item_profit, item_weight) for
            i in range(n_problems)]


def __generate_problem(id: int, items: (int, int), knapsacks: (int, int), knapsack_capacity: (float, float),
                       item_profit: (float, float), item_weight: (float, float)):
    n_knapsacks = np.random.randint(*knapsacks)
    n_items = np.random.randint(*items)
    knapsack_capacities = np.random.uniform(*knapsack_capacity, n_knapsacks)
    item_profits = np.random.uniform(*item_profit, n_items)
    item_weights = np.random.uniform(*item_weight, n_items)

    n_vars = n_items * n_knapsacks  # x_ij
    c = -np.tile(item_profits, n_knapsacks)  # convert to minimiz. problem

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
    return Problem(
        name=f"random_MKP_{id}",
        c=c,
        lb=[0] * n_vars,
        ub=[1] * n_vars,
        types=types,
        b=b,
        A=A
    )