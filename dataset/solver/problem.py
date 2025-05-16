from docplex.mp.model import Model
from docplex.mp.linear import LinearConstraintType, ComparisonType, ConstantExpr, LinearExpr
from datetime import datetime
import docplex
import numpy as np

from docplex.mp.solution import SolveSolution


class Problem:
    def __init__(self, name, c, lb, ub, constraint_types, b, A, var_types=None, model=None):
        self.name = name
        self.c = c
        self.lb = lb
        self.ub = ub
        self.constraint_types = constraint_types
        self.var_types = var_types if var_types is not None else ['B'] * len(c) # assuming binary
        self.b = b
        self.A = A

        self.model = model # keep it cached

    @staticmethod
    def from_model(model: Model):
        name = model.name
        var_indices = {var: i for i, var in enumerate(model.iter_variables())}

        constraints = list(model.iter_constraints())
        n_constraints = len(constraints)
        n_vars = len(var_indices.keys())

        A = np.zeros((n_constraints, n_vars))
        b = np.zeros(n_constraints)

        constraint_types = []
        for i, con in enumerate(constraints):
            if con.sense == ComparisonType.LE:
                constraint_types.append("L")
            elif con.sense == ComparisonType.GE:
                constraint_types.append("G")
            elif con.sense == ComparisonType.EQ:
                constraint_types.append("E")
            else:
                raise Exception(f"Unknown constraint type {con}")
            
            expr = con.lhs
            for var, coef in expr.iter_terms():
                j = var_indices[var]
                A[i, j] = coef
            
            b[i] = con.rhs.constant
        
        c = np.zeros(n_vars)
        obj = model.objective_expr
        if obj.is_constant():
            raise Exception("Objective function is constant")
        
        for var, coef in obj.iter_terms():
            j = var_indices[var]
            c[j] = coef

        if not model.is_minimized():
            c = -c
        
        var_types = []
        lb = np.zeros(n_vars)
        ub = np.zeros(n_vars)

        for idx, var in enumerate(model.iter_variables()):
            if var.is_binary():
                var_types.append('B')
            elif var.is_integer():
                var_types.append('I')
            elif var.is_continuous():
                var_types.append('C')
            else:
                raise Exception(f"Unknown variable type for variable {idx}: {var}")
            
            lb[idx] = var.lb if var.lb is not None else -np.inf
            ub[idx] = var.ub if var.ub is not None else np.inf

        # assert that variable and constraint types corresponds
        problem = Problem(name, c, lb, ub, constraint_types, b, A, var_types, model)
        assert problem.A.shape == (n_constraints, n_vars)
        assert problem.c.shape == (n_vars,)
        assert problem.b.shape == (n_constraints,)
        return problem

    def solve_with_sb(self,max_candidates=10, logged=False):
        model = self.__build_model() if self.model is None else self.model

        from solver.branching.strong_branching import StrongBranching
        sb_callback : StrongBranching = model.register_callback(StrongBranching)
        sb_callback.A = self.A
        sb_callback.b = self.b
        sb_callback.c = self.c
        sb_callback.max_branching_candidates = max_candidates

        start = datetime.now()
        solution : SolveSolution = model.solve(log_output=False)
        end = datetime.now()

        assert solution is not None

        stats = {
            'time': (end - start).total_seconds(),
            'n_vars': len(self.c),
            'n_constraints': len(self.b),
            'name': self.name,
            'sb_decision': sb_callback.tot_branches,
            'gap': sb_callback.optimality_gap,
        }
        return sb_callback.dataset, stats

    def solve_with_learned_sb(self, regressor, max_candidates=10, logged=False):
        model = self.__build_model() if self.model is None else self.model
        from solver.branching.learned_strong_branching import LearnedStrongBranching
        sb_callback = model.register_callback(LearnedStrongBranching)
        sb_callback.max_branching_candidates = max_candidates
        sb_callback.regressor = regressor

        start = datetime.now()
        solution: SolveSolution = model.solve(log_output=logged)
        end = datetime.now()

        assert solution is not None

        stats = {
            'time': (end - start).total_seconds(),
            'sb_decision': sb_callback.tot_branches,
        }
        return stats

    def __build_model(self):
        model = Model(name=self.name)

        n_vars = len(self.c)
        x = []
        for i in range(n_vars):
            if self.var_types[i] == 'B':
                x.append(model.binary_var(name=f"x_{i}"))
            elif self.var_types[i] == 'C':
                x.append(model.continuous_var(lb=self.lb[i], ub=self.ub[i], name=f"x_{i}"))

        model.minimize(model.dot(x, self.c))

        n_constraints = len(self.b)
        if n_constraints != len(self.constraint_types):
            raise Exception( f"Number of constraints ({n_constraints}) doesn't match number of types ({len(self.constraint_types)})")

        n_constraints = len(self.constraint_types)
        for i in range(n_constraints):
            if self.constraint_types[i] == 'E':
                model.add_constraint(model.dot(x, self.A[i]) == self.b[i])
            elif self.constraint_types[i] == 'G':
                model.add_constraint(model.dot(x, self.A[i]) >= self.b[i])
            elif self.constraint_types[i] == 'L':
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

        return model

    def __repr__(self):
        return f"Problem(name={self.name})"
