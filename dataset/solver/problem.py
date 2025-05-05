from docplex.mp.model import Model


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

    def add_branching_callback(self, model: Model, max_candidates=10, logged=False):
        from dataset.solver.strong_branching_callback import StrongBranchCallback
        sb_callback : StrongBranchCallback = model.register_callback(StrongBranchCallback)
        sb_callback.A = self.A
        sb_callback.b = self.b
        sb_callback.c = self.c

        sb_callback.strong_branching_candidates = max_candidates

        model.parameters.mip.interval = 1  # Check nodes frequently
        # model.parameters.mip.strategy.variableselect = 3  # Use strong branching for CPLEX's own decisions

        solution = model.solve(log_output=logged)
        assert solution is not None
        model.report()

        return sb_callback

    def solve(self):
        model = Model(name=self.name)

        # Add variables
        n_vars = len(self.c)
        x = model.binary_var_list(n_vars, name='x')

        model.minimize(model.sum(x[i] * self.c[i] for i in range(n_vars)))

        n_constraints = len(self.b)
        if n_constraints != len(self.types):
            raise Exception( f"Number of constraints ({n_constraints}) doesn't match number of types ({len(self.types)})")

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

        model.parameters.timelimit = 5

        # Disable heuristics
        model.parameters.mip.strategy.heuristicfreq = -1

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

        # Disable pre-solve
        model.parameters.preprocessing.presolve = 'off'
        model.parameters.preprocessing.aggregator = -1
        model.parameters.preprocessing.repeatpresolve = -1

        # Set branching strategy
        model.parameters.mip.strategy.variableselect = 3  # strong

        # Solve the model
        self.add_branching_callback(model)
