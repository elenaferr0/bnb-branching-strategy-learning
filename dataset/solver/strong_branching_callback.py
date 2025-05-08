from collections import defaultdict
from typing import Dict, List

import cplex.callbacks as cpx_cb
import docplex.mp.model
import math
import numpy as np
from docplex.mp.callbacks.cb_mixin import *
import pandas as pd
from docplex.mp.relax_linear import LinearRelaxer
from docplex.mp.solution import SolveSolution

from solver.features import compute_features


class StrongBranchCallback(ModelCallbackMixin, cpx_cb.BranchCallback):
    def __init__(self, env):
        cpx_cb.BranchCallback.__init__(self, env)
        ModelCallbackMixin.__init__(self)
        self.nb_called = 0

        # problem data, kept here for computing features
        self.A = None
        self.b = None
        self.c = None

        self.dataset = pd.DataFrame()

        self.strong_branching_candidates = 5  # TODO: remove this limit

    def __call__(self):
        self.nb_called += 1
        br_type = self.get_branch_type()

        if br_type == self.branch_type.SOS1 or br_type == self.branch_type.SOS2:
            return

        x = self.get_values()
        obj_val = self.get_objective_value()
        coeffs = self.get_objective_coefficients()

        fractional_vars = self.__get_fractional_vars(x, coeffs)

        if not fractional_vars:
            return

        best_var, best_x_i_floor, best_score = self.__get_branching_variable(fractional_vars, obj_val)

        if best_var < 0:  # No good branching candidate
            return

        dv = self.index_to_var(best_var)
        print(f'---> STRONG BRANCH[{self.nb_called}] on var={dv}, score={best_score:.4e}')
        self.make_branch(obj_val, variables=[(best_var, "L", best_x_i_floor + 1)],
                         node_data=(best_var, best_x_i_floor, "UP"))
        self.make_branch(obj_val, variables=[(best_var, "U", best_x_i_floor)],
                         node_data=(best_var, best_x_i_floor, "DOWN"))

    def __get_branching_variable(self, fractional_vars, obj_val):
        # sort by closest to 0.5 and obj coefficient
        fractional_vars.sort(key=lambda v: (-abs(v[2] - 0.5), -abs(v[3])))
        candidates = fractional_vars[:min(self.strong_branching_candidates, len(fractional_vars))]

        best_score = float('-inf')
        best_var = -1
        best_x_i_floor = -1

        for i, x_i, _, _ in candidates:
            down_bound = self.__solve_relaxed_subproblem(i, x_i, "DOWN")
            up_bound = self.__solve_relaxed_subproblem(i, x_i, "UP")

            down_degradation = down_bound - obj_val
            up_degradation = up_bound - obj_val

            score = (down_degradation * up_degradation) / np.abs(obj_val)

            if score > best_score:
                best_score = score
                best_var = i
                best_x_i_floor = math.floor(x_i)

            if score > 0 and score != float('inf'):
                features = compute_features(i, self.A, self.b, self.c)
                features['score'] = np.log(score)
                row = pd.DataFrame.from_dict(features, orient='index').T
                self.dataset = pd.concat([self.dataset, row], ignore_index=True)

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

    def __get_fractional_vars(self, x, c):
        fractional_vars = []
        feasibilities = self.get_feasibilities()
        for j in range(len(x)):
            if feasibilities[j] == self.feasibility_status.infeasible:
                frac_value = x[j] - math.floor(x[j])
                if 0.01 < frac_value < 0.99:  # Ensure variable is truly fractional
                    fractional_vars.append((j, x[j], frac_value, c[j]))
        return fractional_vars
