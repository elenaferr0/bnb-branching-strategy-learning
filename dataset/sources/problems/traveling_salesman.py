from itertools import combinations
import numpy as np
from dataset.solver.problem import Problem

"""
Formulation
min sum_{i in I} sum_{j = 1, j != i}^n c_{ij} x_{ij}
s.t.
    sum_{j = 1, j != i}^n x_{ij} = 1 forall i - outgoing edge
    sum_{i = 1, i != j}^n x_{ij} = 1 forall j - incoming edge
    sum_{i in S} sum_{j not in S, j != i} x_{ij} >= 1 forall S - subtour elimination
    x_{ij} in {0, 1} forall i, j

    S (subtour) is a subset of nodes {1, 2, ..., n} : 2 <= |S| <= n - 1
    c_ij is the cost of traveling from i to j
"""


def traveling_salesman(n_problems: int, cities: (int, int)):
    return [__generate_problem(i, cities) for i in range(n_problems)]


def __generate_problem(id: int, cities: (int, int)):
    n_cities = np.random.randint(*cities)

    # symmetric cost matrix
    costs = np.random.randint(1, 100, size=(n_cities, n_cities))
    for i in range(n_cities):
        costs[i][i] = 0  # no cost to travel to itself
        for j in range(i + 1, n_cities):
            costs[i][j] = costs[j][i]

    n_vars = n_cities * (n_cities - 1)  # x_{ij} for i != j
    c = costs[
        np.repeat(np.arange(n_cities), n_cities - 1),
        np.array([j for i in range(n_cities) for j in range(n_cities) if i != j])
    ]

    A, b, types = [], [], []

    ## constraints
    # sum_{j = 1, j != i}^n x_{ij} = 1 forall i - outgoing edge
    for i in range(n_cities):
        row = np.zeros(n_vars)
        for j in range(n_cities):
            if i != j:
                row[i * (n_cities - 1) + j - (j > i)] = 1
        A.append(row)
        b.append(1)
        types.append('E')

    # sum_{i = 1, i != j}^n x_{ij} = 1 forall j - incoming edge
    for j in range(n_cities):
        row = np.zeros(n_vars)
        for i in range(n_cities):
            if i != j:
                row[j * (n_cities - 1) + i - (i > j)] = 1
        A.append(row)
        b.append(1)
        types.append('E')

    # subtour elimination constraints
    for size in range(2, n_cities - 1):
        for S in combinations(range(n_cities), size):
            row = np.zeros(n_vars)
            for i in S:
                for j in range(n_cities):
                    if j not in S and i != j:
                        row[i * (n_cities - 1) + j - (j > i)] = 1
            A.append(row)
            b.append(1)
            types.append('G')

    A = np.array(A)
    b = np.array(b)
    types = np.array(types)
    return Problem(
        name=f"random_TSP_{id}",
        c=c,
        lb=[0] * n_vars,
        ub=[1] * n_vars,
        types=types,
        b=b,
        A=A
    )