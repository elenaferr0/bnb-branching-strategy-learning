from collections import defaultdict

import numpy as np
from docplex.mp.callbacks.cb_mixin import ModelCallbackMixin
from docplex.mp.model import Model
import cplex.callbacks as cpx_cb

from dataset.generated.strong_branching_callback import StrongBranchCallback

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

class Problem:
    def __init__(self, name, c, lb, ub, types, b, A):
        self.name = name
        self.c = c
        self.lb = lb
        self.ub = ub
        self.types = types
        self.b = b
        self.A = A
        self.solution = None

    def solve(self):
        model = Model(name=self.name)

        # Add variables
        n_vars = len(self.c)
        x = model.binary_var_list(n_vars, name='x')

        model.minimize(model.sum(x[i] * self.c[i] for i in range(n_vars)))

        # Add constraints
        n_constraints = len(self.types)
        for i in range(n_constraints):
            row = self.A[i]
            sense = self.types[i]
            rhs = self.b[i]
            lhs = model.sum(row[j] * x[j] for j in range(n_vars))
            if sense == 'L':
                model.add_constraint(lhs <= rhs)
            elif sense == 'G':
                model.add_constraint(lhs >= rhs)
            elif sense == 'E':
                model.add_constraint(lhs == rhs)

        # Set time limit
        model.parameters.timelimit = 5

        # Disable heuristics (Docplex doesn't have a direct equivalent to CPX_PARAM_HEURFREQ -1)
        model.parameters.mip.strategy.heuristicfreq = -1 # Setting to -1 might not be the exact same as CPX

        # Disable cuts (Docplex parameters might have slightly different names or groupings)
        model.parameters.mip.cuts.bqp = -1
        model.parameters.mip.cuts.cliques = -1
        model.parameters.mip.cuts.covers = -1
        model.parameters.mip.cuts.disjunctive = -1
        model.parameters.mip.cuts.flowcovers = -1
        model.parameters.mip.cuts.gomory = -1
        model.parameters.mip.cuts.gubcovers = -1
        model.parameters.mip.cuts.implied = -1
        model.parameters.mip.cuts.liftproj = -1
        model.parameters.mip.cuts.localimplied = -1
        model.parameters.mip.cuts.mcfcut = -1
        model.parameters.mip.cuts.mircut = -1
        model.parameters.mip.cuts.nodecuts = -1
        model.parameters.mip.cuts.pathcut = -1
        model.parameters.mip.cuts.rlt = -1
        model.parameters.mip.cuts.zerohalfcut = -1

        model.parameters.mip.strategy.probe = -1 # Equivalent to CPX_PARAM_PROBE -1

        # Disable pre-solve
        model.parameters.preprocessing.presolve = 'off'
        model.parameters.preprocessing.aggregator = -1
        model.parameters.preprocessing.repeatpresolve = -1

        # Set branching strategy
        model.parameters.mip.strategy.variableselect = 3 # strong

        # Solve the model
        add_branching_callback(model)

def add_branching_callback(model, max_candidates=10, logged=False):
    # Register the callback
    sb_callback = model.register_callback(StrongBranchCallback)
    sb_callback.strong_branching_candidates = max_candidates

    # Set parameters for better control
    model.parameters.mip.interval = 1  # Check nodes frequently
    model.parameters.mip.strategy.variableselect = 3  # Use strong branching for CPLEX's own decisions

    # Solve the model
    solution = model.solve(log_output=logged)
    assert solution is not None
    model.report()

    # Report on the branching decisions
    sb_callback.report(n=5)

    return sb_callback

def bin_packing(n_problems: int, items: (int, int), bins: (int, int), bin_capacity: (float, float),
                item_size: (float, float)):
   return [__generate_problem(i, items, bins, bin_capacity, item_size) for i in range(n_problems)]


def __generate_problem(id: int, items: (int, int), bins: (int, int), bin_capacity: (float, float),
                       item_size: (float, float)):
    n_items = np.random.randint(*items)
    n_bins = np.random.randint(*bins)
    bin_capacity = np.random.uniform(*bin_capacity)
    item_sizes = np.random.uniform(*item_size, size=n_items)
    n_vars = n_bins + n_items * n_bins  # y_i + x_{ij}

    c = np.concatenate([
        np.ones(n_bins),  # cost for bins (y_j)
        np.zeros(n_items * n_bins)  # no cost for x_{ij} (multiplying n_items * n_bins as x has 2 indexes)
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
        row[j] = -bin_capacity  # coefficient for y_j
        for i in range(n_items):
            row[n_bins + i * n_bins + j] = item_sizes[i]  # coefficient for x_{ij}
        A.append(row)
        b.append(0)
        types.append('L')

    # sum(x_ij) = 1 for all i
    for i in range(n_items):
        row = np.zeros(n_vars)
        for j in range(n_bins):
            row[n_bins + i * n_bins + j] = 1  # coefficient for x_{ij}
        A.append(row)
        b.append(1)
        types.append('E')

    A = np.array(A)
    b = np.array(b)
    types = np.array(types)
    bnd = [{"LO": 0, "UP": 1} for _ in range(n_vars)]

    problem = Problem(
        name=f"np.random_BP_{id}",
        c=c,
        lb=[0] * n_vars,
        ub=[1] * n_vars,
        types=types,
        b=b,
        A=A
    )
    vars = problem.solve()
    return f"np.random_BP_{id}", types, c, A, b, bnd, vars

if __name__ == "__main__":
    bp = bin_packing(
        n_problems=1,
        items=(3, 4),
        bins=(10, 20),
        bin_capacity=(3, 4),
        item_size=(1, 2),

        # n_problems=1,
        # items=(100, 300),
        # bins=(50, 150),
        # bin_capacity=(50, 100),
        # item_size=(10, 60),
    )
    print(bp)
