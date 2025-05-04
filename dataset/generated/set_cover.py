import numpy as np

from dataset.generated.problem import Problem

"""
Formulation
min sum_{s in S} x_s
s.t. sum_{s: e in s} x_s >= 1 forall e in E
x in {0,1}^n
"""

A_DENSITY = 0.3


def set_cover(n_problems: int, sets: (int, int), elements: (int, int)):
    return [__generate_problem(i, sets, elements) for i in range(n_problems)]


def __generate_problem(id: int, sets: (int, int), elements: (int, int)):
    n_sets = np.random.randint(*sets)
    n_elements = np.random.randint(*elements)

    c = np.ones(n_sets)

    A = (np.random.rand(n_elements, n_sets) < A_DENSITY).astype(int)

    for j in range(n_sets): # ensure each element is covered by at least one set
        if np.sum(A[:, j]) == 0:
            i = np.random.randint(0, n_elements - 1)
            A[i, j] = 1

    b = np.ones(n_elements) # each element must be covered
    types = ['G'] * n_sets  # greater than

    problem = Problem(
        name=f"random_SC_{id}",
        c=c,
        lb=[0] * n_sets,
        ub=[1] * n_sets,
        types=types,
        b=b,
        A=A
    )

    problem.solve()
    return problem

if __name__ == "__main__":
    problems = set_cover(1, (5, 15), (5, 15))
    for problem in problems:
        print(problem.name)
        # print("Objective coefficients:", problem.c)
        # print("Constraints matrix:\n", problem.A)
        # print("Right-hand side:", problem.b)
        # print("Variable types:", problem.types)
        # print("Bounds:", problem.lb, problem.ub)