import re, os
import tsplib95
import numpy as np

from dataset.solver import Problem


def tsp_to_standard_form(name, distance_matrix):
    # Using the Miller-Tucker-Zemlin (MTZ) formulation for TSP
    n = distance_matrix.shape[0]

    # Decision variables:
    # - x[i,j] = 1 if we travel from i to j, 0 otherwise (n^2 binary variables)
    # - u[i] = position of city i in the tour (n continuous variables)
    # Total variables: n^2 + n

    # Objective: minimize sum of distances
    c = np.zeros(n*n + n)
    for i in range(n):
        for j in range(n):
            if i != j:
                c[i*n + j] = distance_matrix[i, j]

    # Constraints:
    # 1. Each city must be visited exactly once (n equality constraints)
    # 2. Each city must be departed from exactly once (n equality constraints)
    # 3. Subtour elimination constraints using MTZ formulation ((n-1)*(n-2) inequality constraints)
    # 4. u[0] = 1 (1 equality constraint)
    # Total constraints: 2n + (n-1)*(n-2) + 1

    # Number of constraints
    num_constraints = 2*n + (n-1)*(n-2) + 1

    # Initialize constraint matrix A, right-hand-side b, and constraint types
    A = np.zeros((num_constraints, n*n + n))
    b = np.zeros(num_constraints)
    constraint_types = []

    # Constraint type 1: Each city must be visited exactly once
    row = 0
    for j in range(n):
        for i in range(n):
            if i != j:
                A[row, i*n + j] = 1
        b[row] = 1
        constraint_types.append('E')  # Equality constraint
        row += 1

    # Constraint type 2: Each city must be departed from exactly once
    for i in range(n):
        for j in range(n):
            if i != j:
                A[row, i*n + j] = 1
        b[row] = 1
        constraint_types.append('E')  # Equality constraint
        row += 1

    # Constraint type 3: Subtour elimination using MTZ
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                # u[i] - u[j] + n*x[i,j] <= n-1
                A[row, n*n + i] = 1
                A[row, n*n + j] = -1
                A[row, i*n + j] = n
                b[row] = n - 1
                constraint_types.append('L')  # Less than or equal constraint
                row += 1

    # Constraint type 4: Set u[0] = 1
    A[row, n*n] = 1
    b[row] = 1
    constraint_types.append('E')  # Equality constraint
    row += 1

    # Set lower and upper bounds for x[i,j] and u[i]
    lb = np.zeros(n*n + n)
    ub = np.ones(n*n + n)

    # Diagonal elements of x matrix are 0 (no self-loops)
    for i in range(n):
        lb[i*n + i] = 0
        ub[i*n + i] = 0

    # u[i] values range from 1 to n
    for i in range(n):
        lb[n*n + i] = 1
        ub[n*n + i] = n

    # Variable types: binary for x[i,j], continuous for u[i]
    var_types = ['B'] * (n*n) + ['C'] * n

    return Problem(
        name=name,
        A=A,
        b=b,
        c=c,
        lb=lb,
        ub=ub,
        constraint_types=constraint_types,
        var_types=var_types,
    )

def load_tsplib():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tsplib_path = os.path.join(current_dir, "tsplib")

    problems = []
    for filename in os.listdir(tsplib_path):
        if filename.endswith(".tsp"):
            tsplib_prob = tsplib95.load(os.path.join(tsplib_path, filename))
            n_nodes = tsplib_prob.dimension
            problem = tsp_to_standard_form(tsplib_prob.name, tsplib_prob.get_weight(0, n_nodes))
            problems.append(tsplib_prob)
    return problems

if __name__ == "__main__":
    probs = load_tsplib()
    print(probs)
