from collections import defaultdict
from datetime import datetime
import numpy as np
from pyscipopt import Model, quicksum, SCIP_PARAMSETTING
from pyscipopt import Branchrule
from pyscipopt.scip import Term
from pyscipopt.scip import Solution

from learned_strong_branching import LearnedStrongBranching
from strong_branching import StrongBranchingRule

MAX_BRANCHING_PRIORITY = 99999
LEARNED_STRONG_BRANCHING = "learnedstrongbrnch"
RELIABILITY_BRANCHING = "relpscost"
PSEUDO_COST_BRANCHING = "pscost"
MOST_INFEASIBLE_BRANCHING = "mostinf"
RANDOM_BRANCHING = "random"

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

    @staticmethod
    def from_model(path, name):
        model = Model()
        model.readProblem(path)
        model.setProbName(name)

        variables = model.getVars()
        constraints = model.getConss()

        # Initialize data structures
        n_vars = len(variables)
        n_cons = len(constraints)

        # Create mapping from variable to index
        c = np.zeros(n_vars)

        # Extract objective coefficients (vector c)
        for i, var in enumerate(variables):
            c[i] = model.getObjective().terms.get(Term(var), 0.0)

        variables = model.getVars()
        num_vars = len(variables)

        # Initialize A and b
        A = []
        b = []

        all_constraints = model.getConss()

        for con in all_constraints:
            assert con.isLinear(), "Only linear constraints are supported"

            # Get coefficients for this linear constraint
            coeffs = model.getValsLinear(con)

            # Create a row for the A matrix
            row = [0.0] * num_vars
            for var, coeff in coeffs.items():
                v = list(filter(lambda x: x.name == var, model.getVars()))[0]
                try:
                    # Find the index of the variable in our ordered list
                    var_index = v.getIndex()
                    row[var_index] = coeff
                except ValueError:
                    # This case should ideally not happen if getVars() gets all relevant variables,
                    # but it's good practice to handle unexpected variables.
                    print(
                        f"Warning: Variable {var.getName()} found in constraint {con.getName()} but not in model's getVars() list.")
                    pass

            rhs = model.getRhs(con)
            A.append(row)
            b.append(rhs)

        A = np.array(A)
        b = np.array(b)
        # lb, ub, constraint_types, and var_types are not needed if the model is already built
        return Problem(name, c=c, lb=[], ub=[], constraint_types=[], b=b, A=A, var_types=[], model=model)

    def solve_with_sb(self, logged=False):
        if self.model is None:
            self.build_model()
        self.basic_config(logged=logged)
        self.disable_configs()
        sb = StrongBranchingRule(self.model, self.A, self.b, self.c, logged)
        self.model.includeBranchrule(            sb,
            "customstrbrnch",
            "Custom strong branching rule for learning",
            priority=MAX_BRANCHING_PRIORITY,
            maxbounddist=1.0
        )
        self.model.optimize()
        assert self.model.getStatus() == "optimal", f"Model {self.model.getProbName()} did not solve to optimality. Status: {self.model.getStatus()}"

        stats = {            
            'time': self.model.getSolvingTime(),
            'n_vars': len(self.c),
            'n_constraints': len(self.b),
            'name': self.name,
            'n_nodes': sb.model.getNNodes(),
            'gap': sb.model.getGap(),
        }
        self.model.freeProb()
        return sb.dataset, stats

    def solve_with_rule(self, branching_strategy, predictor=None, predictor_name=None, logged=False, max_nodes=-1, timelimit=-1):
        if self.model is None:
            self.build_model()
        self.basic_config(logged=logged)
        self.disable_configs()

        if branching_strategy == LEARNED_STRONG_BRANCHING:
            assert predictor is not None, "Predictor must be provided for learned strong branching"
            assert predictor_name is not None, "Predictor name must be provided for learned strong branching"
            self.model.includeBranchrule(
                LearnedStrongBranching(self.model, predictor, self.A, self.b, self.c, logged),
                LEARNED_STRONG_BRANCHING,
                "Learned Strong Branching Rule",
                priority=MAX_BRANCHING_PRIORITY,
                maxdepth=-1,  # No depth limit
                maxbounddist=1.0
            )
        else:
            self.model.setIntParam(f'branching/{branching_strategy}/priority', MAX_BRANCHING_PRIORITY)

        self.model.setLongintParam('limits/nodes', max_nodes if max_nodes > 0 else -1)
        self.model.setRealParam('limits/time', timelimit if timelimit > 0 else -1)
        try:
            self.model.optimize()
        except Exception as e:
            print(f"Error during optimization: {e}")
            return None

        stats = {
            'time': self.model.getSolvingTime(),
            'n_vars': len(self.c),
            'n_constraints': len(self.b),
            'name': self.name,
            'n_nodes': self.model.getNNodes(),
            'gap': self.model.getGap(),
            'status': self.model.getStatus(),
            'time_limit': timelimit if timelimit > 0 else -1,
            'node_limit': max_nodes if max_nodes > 0 else -1,
            'strategy': branching_strategy,
            'predictor': predictor_name if branching_strategy == LEARNED_STRONG_BRANCHING else None
        }
        return stats

    def build_model(self, disable_cuts=True, disable_heuristics=True, disable_presolving=True):
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

        assert (model.getNConss() == len(
            self.A)), "Number of constraints in model doesn't match number of constraints in problem"
        assert (model.getNConss() == len(
            self.b)), "Number of constraints in model doesn't match number of constraints in problem"
        assert (model.getNVars() == len(
            self.c)), "Number of variables in model doesn't match number of variables in problem"
        self.model = model

    def basic_config(self, logged=False, max_nodes=-1, timelimit=-1):
        if self.model is None:
            raise Exception("Model is not built yet. Call __build_model() first.")

        if not logged:
            self.model.hideOutput()
            self.model.setIntParam('display/verblevel', 0)  # Quiet mode
        else:
            self.model.setIntParam('display/verblevel', 3)  # Verbose output

        if max_nodes > 0:
            self.model.setIntParam('limits/nodes', max_nodes)

        if timelimit > 0:
            self.model.setRealParam('limits/time', timelimit)

        self.model.setIntParam('display/freq', 500)  # logging frequency

    def disable_configs(self):
        self.model.setPresolve(SCIP_PARAMSETTING.OFF)
        self.model.setSeparating(SCIP_PARAMSETTING.OFF)
        self.model.setHeuristics(SCIP_PARAMSETTING.OFF)

    def __repr__(self):
        return f"Problem(name={self.name})"

