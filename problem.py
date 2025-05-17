from datetime import datetime
import numpy as np
from pyscipopt import Model, quicksum
from pyscipopt import Branchrule
from pyscipopt.scip import Solution

from strong_branching import StrongBranchingRule

class Problem:
    def __init__(self, name, c, lb, ub, constraint_types, b, A, var_types=None, model=None):
        self.name = name
        self.c = c
        self.lb = lb
        self.ub = ub
        self.constraint_types = constraint_types
        self.var_types = var_types if var_types is not None else ['B'] * len(c)  # assuming binary
        self.b = b
        self.A = A

        self.model = model

    def solve_with_sb(self, logged=False):
        model = self.__build_model() if self.model is None else self.model
        if not logged:
            model.hideOutput()
            model.setIntParam('display/verblevel', 0)  # Quiet mode
        else:
            model.setIntParam('display/verblevel', 3)  # Verbose output

        sb = StrongBranchingRule(model, self.A, self.b, self.c, logged)

        model.includeBranchrule(
            sb,
            "strongbranching",
            "Custom strong branching rule for learning",
            priority=1000000,  # High priority to ensure it's used
            maxdepth=-1,  # No depth limit
            maxbounddist=1.0
        )

        start = datetime.now()
        model.optimize()
        end = datetime.now()

        assert model.getStatus() == "optimal", f"Model {model.getProbName()} did not solve to optimality. Status: {model.getStatus()}"

        stats = {
            'time': (end - start).total_seconds(),
            'n_vars': len(self.c),
            'n_constraints': len(self.b),
            'name': self.name,
            'sb_decision': sb.model.getNNodes(),
            'gap': sb.model.getGap(),
        }
        return sb.dataset, stats

    def solve_with_learned_sb(self, regressor, logged=False):
        model = self.__build_model() if self.model is None else self.model

        # Create and register the branching rule
        # sb_callback = LearnedStrongBranchingRule()
        # model.includeBranchrule(
        #     sb_callback,
        #     "learnedstrongbranching",
        #     "Learned strong branching rule",
        #     priority=1000000,  # High priority to ensure it's used
        #     maxdepth=-1,       # No depth limit
        #     maxbounddist=1.0
        # )

        start = datetime.now()

        model.optimize()
        end = datetime.now()

        stats = {
            'time': (end - start).total_seconds(),
            # 'sb_decision': sb_callback.tot_branches,
        }
        return stats

    def __build_model(self):
        model = Model(self.name)
        n_vars = len(self.c)
        x = []
        for i in range(n_vars):
            if self.var_types[i] == 'B':
                x.append(model.addVar(name=f"x_{i}", vtype="B"))
            elif self.var_types[i] == 'C':
                x.append(model.addVar(name=f"x_{i}", vtype="C", lb=self.lb[i], ub=self.ub[i]))

        # Set objective function
        model.setObjective(quicksum(self.c[i] * x[i] for i in range(n_vars)), "minimize")

        n_constraints = len(self.b)
        if n_constraints != len(self.constraint_types):
            raise Exception(
                f"Number of constraints ({n_constraints}) doesn't match number of types ({len(self.constraint_types)})")

        # Add constraints
        for i in range(n_constraints):
            lhs = quicksum(self.A[i][j] * x[j] for j in range(n_vars) if self.A[i][j] != 0)

            if self.constraint_types[i] == 'E':
                model.addCons(lhs == self.b[i])
            elif self.constraint_types[i] == 'G':
                model.addCons(lhs >= self.b[i])
            elif self.constraint_types[i] == 'L':
                model.addCons(lhs <= self.b[i])

        # Disable cuts
        model.setIntParam('separating/maxrounds', 0)
        model.setIntParam('separating/maxroundsroot', 0)

        # Disable various cutting plane methods
        cut_types = [
            'separating/clique', 'separating/gomory', 'separating/strongcg',
            'separating/cmir', 'separating/flowcover', 'separating/mcf', 'separating/zerohalf',
        ]
        for cut_type in cut_types:
            model.setIntParam(f'{cut_type}/freq', -1)

        # Disable heuristics
        model.setIntParam('heuristics/dps/freq', -1)

        # Disable presolving
        model.setBoolParam('lp/presolving', False)
        model.setBoolParam('concurrent/presolvebefore', False)
        model.setBoolParam('presolving/donotmultaggr', True)

        presolving = [
            "presolving/maxrounds",
            "presolving/trivial/maxrounds",
            "presolving/inttobinary/maxrounds",
            "presolving/gateextraction/maxrounds",
            "presolving/dualcomp/maxrounds",
            "presolving/domcol/maxrounds",
            "presolving/implics/maxrounds",
            "presolving/sparsify/maxrounds",
            "presolving/dualsparsify/maxrounds",
            "propagating/dualfix/maxprerounds",
            "propagating/genvbounds/maxprerounds",
            "propagating/obbt/maxprerounds",
            "propagating/nlobbt/maxprerounds",
            "propagating/probing/maxprerounds",
            "propagating/pseudoobj/maxprerounds",
            "propagating/redcost/maxprerounds",
            "propagating/rootredcost/maxprerounds",
            "propagating/symmetry/maxprerounds",
            "propagating/vbounds/maxprerounds",
            "propagating/maxrounds",
            "propagating/maxroundsroot",
            "constraints/cardinality/maxprerounds",
            "constraints/SOS1/maxprerounds",
            "constraints/SOS2/maxprerounds",
            "constraints/varbound/maxprerounds",
            "constraints/knapsack/maxprerounds",
            "constraints/setppc/maxprerounds",
            "constraints/linking/maxprerounds",
            "constraints/or/maxprerounds",
            "constraints/and/maxprerounds",
            "constraints/xor/maxprerounds",
            "constraints/conjunction/maxprerounds",
            "constraints/disjunction/maxprerounds",
            "constraints/linear/maxprerounds",
            "constraints/orbisack/maxprerounds",
            "constraints/orbitope/maxprerounds",
            "constraints/symresack/maxprerounds",
            "constraints/logicor/maxprerounds",
            "constraints/bounddisjunction/maxprerounds",
            "constraints/cumulative/maxprerounds",
            "constraints/nonlinear/maxprerounds",
            "constraints/pseudoboolean/maxprerounds",
            "constraints/superindicator/maxprerounds",
            "constraints/indicator/maxprerounds",
            "constraints/components/maxprerounds",
            "presolving/maxrestarts",
            "presolving/maxrounds",
        ]

        for presolve in presolving:
            model.setIntParam(presolve, 0)

        # Check nodes frequently
        model.setIntParam('display/freq', 1)

        assert(model.getNConss() == len(self.A)), "Number of constraints in model doesn't match number of constraints in problem"
        assert(model.getNConss() == len(self.b)), "Number of constraints in model doesn't match number of constraints in problem"
        assert(model.getNVars() == len(self.c)), "Number of variables in model doesn't match number of variables in problem"
        return model

    def __repr__(self):
        return f"Problem(name={self.name})"
