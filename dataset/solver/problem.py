import pandas as pd
from docplex.mp.model import Model
from datetime import datetime

from docplex.mp.solution import SolveSolution


class Problem:
    def __init__(self, name, c, lb, ub, types, b, A):
        self.name = name
        self.c = c
        self.lb = lb
        self.ub = ub
        self.types = types
        self.b = b
        self.A = A

    def __solve_with_sb(self, model: Model, max_candidates=10, logged=False):
        from solver.strong_branching_callback import StrongBranchCallback
        sb_callback : StrongBranchCallback = model.register_callback(StrongBranchCallback)
        sb_callback.A = self.A
        sb_callback.b = self.b
        sb_callback.c = self.c
        sb_callback.strong_branching_candidates = max_candidates

        start = datetime.now()
        solution : SolveSolution = model.solve(log_output=logged)
        end = datetime.now()

        assert solution is not None

        stats = {
            'time': (end - start).total_seconds(),
            'n_vars': len(self.c),
            'n_constraints': len(self.b),
            'name': self.name,
            'sb_decision': sb_callback.tot_branches,
        }
        return sb_callback.dataset, stats

    def solve(self):
        model = Model(name=self.name)

        n_vars = len(self.c)
        x = model.binary_var_list(n_vars, name='x')

        model.minimize(model.sum(x[i] * self.c[i] for i in range(n_vars)))

        n_constraints = len(self.b)
        if n_constraints != len(self.types):
            raise Exception( f"Number of constraints ({n_constraints}) doesn't match number of types ({len(self.types)})")

        n_constraints = len(self.types)
        for i in range(n_constraints):
            if self.types[i] == 'E':
                model.add_constraint(model.dot(x, self.A[i]) == self.b[i])
            elif self.types[i] == 'G':
                model.add_constraint(model.dot(x, self.A[i]) >= self.b[i])
            elif self.types[i] == 'L':
                model.add_constraint(model.dot(x, self.A[i]) <= self.b[i])

        # model.parameters.timelimit = 5

        # Disable cuts
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

        model.parameters.mip.strategy.probe = -1
        model.parameters.mip.strategy.search = 0 # traditional search
        model.parameters.mip.strategy.presolvenode = -1
        model.parameters.mip.strategy.heuristiceffort = 0 # disable heuristics
        model.parameters.mip.strategy.heuristicfreq = -1

        # Disable pre-solve
        model.parameters.preprocessing.presolve = 0
        model.parameters.preprocessing.aggregator = -1
        model.parameters.preprocessing.repeatpresolve = -1

        model.parameters.mip.interval = 1  # Check nodes frequently

        return self.__solve_with_sb(model, logged=False)

    def __repr__(self):
        return f"Problem(name={self.name})"
