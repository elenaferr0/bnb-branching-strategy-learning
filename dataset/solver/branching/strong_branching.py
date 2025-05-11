from collections import defaultdict

import math
import numpy as np
import pandas as pd
from docplex.mp.relax_linear import LinearRelaxer
from docplex.mp.solution import SolveSolution

from dataset.solver.features import compute_features, Params
from dataset.solver.branching.custom_branching import CustomBranchingCallback

class StrongBranching(CustomBranchingCallback):
    def __init__(self, env):
        super().__init__(env)
        self.tot_branches = 0

        # problem data, kept here for computing features
        self.A = None
        self.b = None
        self.c = None

        self.dataset = pd.DataFrame()
        self.n_branches_by_var = defaultdict(int)

    def _choose_branching_variable(self):
        x = self.get_values()
        c = self.get_objective_coefficients()

        candidates = self._get_branching_candidates(x, c)
        if not candidates:
            return -1, -1, -1

        obj_val = self.get_objective_value()

        best_score = float('-inf')
        best_var = -1
        best_x_i_floor = -1

        for i, x_i, _, _ in candidates:
            down_bound = self.__solve_relaxed_subproblem(i, x_i, "DOWN")
            up_bound = self.__solve_relaxed_subproblem(i, x_i, "UP")

            down_degradation = np.abs(down_bound - obj_val)
            up_degradation = np.abs(up_bound - obj_val)

            score = (down_degradation * up_degradation) / np.abs(obj_val)

            if score > best_score:
                best_score = score
                best_var = i
                best_x_i_floor = np.floor(x_i)

            if score > 0 and score != float('inf'):
                params = Params(
                    var_idx=i,
                    x_i=x_i,
                    node_depth=self.get_current_node_depth(),
                    nr_variables=self.model.number_of_variables,
                    curr_obj=obj_val,
                    down_penalty=down_degradation,
                    up_penalty=up_degradation,
                    n_branches_by_var=self.n_branches_by_var[i],
                    tot_branches=self.tot_branches
                )
                features = compute_features(params, self.A, self.b, self.c)
                features['score'] = np.log(score)
                row = pd.DataFrame.from_dict(features, orient='index').T
                self.dataset = pd.concat([self.dataset, row], ignore_index=True)
                pass

        self.n_branches_by_var[best_var] += 1
        return best_var, best_x_i_floor, best_score

    def __solve_relaxed_subproblem(self, i: int, val, constraint: str):
        rx = LinearRelaxer.make_relaxed_model(self.model, relaxed_name=f"relaxed_{constraint}_{self.model.name}")
        if constraint == "UP":
            rx.add_constraint(rx.get_var_by_index(i) >= math.ceil(val))
        else:
            rx.add_constraint(rx.get_var_by_index(i) <= math.floor(val))
        solution: SolveSolution = rx.solve()
        if solution is None:
            return float('inf')
        else:
            return solution.objective_value