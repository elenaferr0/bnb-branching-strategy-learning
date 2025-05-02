import numpy as np
import random

"""
Formulation
min k = sum_{j in J} y_j
s.t. 
     k >= 1
     sum_{i in I} s(i) x_{ij} <= B y_i forall j in J
     sum_{j in J} x_{ij} = 1 forall i in I
     
     y_j in {0,1} forall j in J
     x_{ij} in {0,1} forall i in I, j in J
     
     x_{ij} in {0,1} forall i in I, j in J
     y_j in {0,1} forall j in J
   
     I: items, J: bins
     s(i): size of item i
     B: bin capacity
"""


def bin_packing(n_problems: int, max_items: int, max_bins: int, max_bin_capacity: float, max_item_size: float):
    return [__generate_problem(i, max_items, max_bins, max_bin_capacity, max_item_size) for i in range(n_problems)]


def __generate_problem(id: int, max_items: int, max_bins: int, max_bin_capacity: float, max_item_size: float):
    n_items = random.randint(1, max_items)
    n_bins = random.randint(1, max_bins)
    bin_capacity = random.uniform(1, max_bin_capacity)
    item_sizes = np.random.uniform(1, max_item_size, size=n_items)
    n_vars = n_bins + n_items * n_bins # y_i + x_{ij}

    c = np.concatenate([
        np.ones(n_bins), # cost for bins (y_j)
        np.zeros(n_items * n_bins) # no cost for x_{ij} (multiplying n_items * n_bins as x has 2 indexes)
    ])

    A, b, types = [], [], []

    ## constraints
    # k >= 1
    A.append(np.concatenate([np.zeros(n_bins), np.ones(n_items * n_bins)]))
    b.append(1)
    types.append('G')

    # sum(s(i) * x_ij) <= B * y_j for all j
    for j in range(n_bins):
        row = np.zeros(n_vars)
        row[j] = -bin_capacity # coefficient for y_j
        for i in range(n_items):
            row[n_bins + i * n_bins + j] = item_sizes[i] # coefficient for x_{ij}
        A.append(row)
        b.append(0)
        types.append('L')

    # sum(x_ij) = 1 for all i
    for i in range(n_items):
        row = np.zeros(n_vars)
        for j in range(n_bins):
            row[n_bins + i * n_bins + j] = 1 # coefficient for x_{ij}
        A.append(row)
        b.append(1)
        types.append('E')

    A = np.array(A)
    b = np.array(b)
    types = np.array(types)
    bnd = [{"LO": 0, "UP": 1} for _ in range(n_vars)]

    return f"random_BP_{id}", types, c, A, b, bnd
