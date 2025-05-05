import numpy as np
import os

from ..solver.problem import Problem


def __load_problem(file_path):
    """
    #Variables (n), #Constraints (m), Optimal value,
    Profit P(j) for each n,
    m x n matrix of constraints,
    Capacity b(i) for each m.
    """
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Parse header: n, m, optimal_value
    header = lines[0].split()
    n_vars = int(header[0])
    n_constraints = int(header[1])

    # Parse profit vector (objective coefficients)
    c = []
    line_idx = 1
    while len(c) < n_vars:
        c.extend([float(val) for val in lines[line_idx].split()])
        line_idx += 1
    c = np.array(c[:n_vars])

    # Parse constraint matrix A
    A = []
    for i in range(n_constraints):
        row = []
        while len(row) < n_vars and line_idx < len(lines):
            row.extend([float(val) for val in lines[line_idx].split()])
            line_idx += 1
        A.append(row[:n_vars])
    A = np.array(A)

    # Parse capacity values (constraint right-hand sides)
    b = []
    while len(b) < n_constraints and line_idx < len(lines):
        b.extend([float(val) for val in lines[line_idx].split()])
        line_idx += 1
    b = np.array(b[:n_constraints])

    # Default: binary variables with <= constraints
    lb = [0] * n_vars
    ub = [1] * n_vars
    types = ['L'] * n_constraints

    # Create problem instance
    name = os.path.basename(file_path).split('.')[0]
    problem = Problem(name=name, c=c, lb=lb, ub=ub, types=types, b=b, A=A)

    return problem


def load_orlib_dataset(folder_path):
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder path {folder_path} does not exist.")
    problems = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.dat'):
            file_path = os.path.join(folder_path, file_name)
            problems.append(__load_problem(file_path))
    return problems
