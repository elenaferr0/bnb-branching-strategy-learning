import numpy as np
import random

"""
Formulation
min sum_{s in S} x_s
s.t. sum_{s: e in s} x_s >= 1 forall e in E
x in {0,1}^n


"""

A_DENSITY = 0.3


def set_cover(n_problems: int, max_sets: int, max_elements: int):
    return [__generate_problem(i, max_sets, max_elements) for i in range(n_problems)]


def __generate_problem(id: int, max_sets: int, max_elements: int):
    n_sets = random.randint(1, max_sets)
    n_elements = random.randint(1, max_elements)

    c = np.ones(n_sets)

    A = (np.random.rand(n_elements, n_sets) < A_DENSITY).astype(int)

    for j in range(n_sets): # ensure each element is covered by at least one set
        if np.sum(A[:, j]) == 0:
            i = random.randint(0, n_elements - 1)
            A[i, j] = 1

    b = np.ones(n_elements) # each element must be covered
    types = ['G'] * n_sets  # greater than
    bnd = [{"LO": 0, "UP": 1} for _ in range(n_sets)]

    return f"random_SC_{id}", types, c, A, b, bnd
