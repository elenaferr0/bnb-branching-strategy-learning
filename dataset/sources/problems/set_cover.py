import numpy as np

from dataset.solver.problem import Problem

"""
Formulation
min sum_{s in S} x_s
s.t. sum_{s: e in s} x_s >= 1 forall e in E
x in {0,1}^n
"""

A_DENSITY = 0.3


def set_cover(n_problems: int, universe_size_range=(50, 70), seed=None):
    if seed is not None:
        np.random.seed(seed)

    return [__generate_problem(i, universe_size_range) for i in range(n_problems)]


def __generate_problem(id: int, universe_size_range):
    # universe selection
    universe_size = np.random.randint(*universe_size_range)
    universe = np.random.choice(list(range(1, 100)), size=universe_size, replace=False)

    binary_matrix = np.random.randint(0, 2, size=(len(universe), len(universe)))

    # Ensure each row and column has at least one 1 to avoid empty sets
    for i in range(binary_matrix.shape[0]):
        if np.sum(binary_matrix[i, :]) == 0:
            binary_matrix[i, np.random.randint(0, binary_matrix.shape[1])] = 1

    for j in range(binary_matrix.shape[1]):
        if np.sum(binary_matrix[:, j]) == 0:
            binary_matrix[np.random.randint(0, binary_matrix.shape[0]), j] = 1

    # mapping to universe elements
    subsets = []
    for j in range(binary_matrix.shape[1]):
        subset = []
        for i in range(binary_matrix.shape[0]):
            if binary_matrix[i, j] == 1:
                subset.append(universe[i])
        subsets.append(subset)

    # remove duplicated sets from subsets
    unique_subsets = []
    for subset in subsets:
        if subset not in unique_subsets:
            unique_subsets.append(subset)

    # shuffling within subsets
    for i in range(len(unique_subsets)):
        np.random.shuffle(unique_subsets[i])

    # Create Problem object
    n_subsets = len(unique_subsets)
    n_elements = len(universe)

    A = np.zeros((n_elements, len(unique_subsets)))
    for j, subset in enumerate(unique_subsets):
        for elem in subset:
            i, = np.where(universe == elem)
            A[i, j] = 1

    c = np.ones(len(unique_subsets))
    b = np.ones(n_elements)
    types = ['G'] * n_elements

    return Problem(
        name=f"SC_{id}",
        c=c,
        lb=[0] * n_subsets,
        ub=[1] * n_subsets,
        types=types,
        b=b,
        A=A,
    )
