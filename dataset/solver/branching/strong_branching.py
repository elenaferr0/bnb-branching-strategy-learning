from collections import defaultdict

import math
import numpy as np
import pandas as pd
from docplex.mp.relax_linear import LinearRelaxer
from docplex.mp.solution import SolveSolution

from solver.features import compute_features, Params
from solver.branching.custom_branching import CustomBranching

class StrongBranching(CustomBranching):
    def __init__(self, env, A=None, b=None, c=None):
        super().__init__(env)
        self.tot_branches = 0
        # problem data, kept here for computing features
        self.A = A
        self.b = b
        self.c = c
        self.dataset = pd.DataFrame()
        self.n_branches_by_var = defaultdict(int)
        self.relaxation_cache = {}
        self.max_cache_size = 100
        self.penalty_for_infeasibility = 1e6

    def _choose_branching_variable(self):
        x = self.get_values()
        c = self.get_objective_coefficients()
        candidates = self._get_branching_candidates(x, c)

        if not candidates:
            return -1, -1, -1, False

        obj_val = self.get_objective_value()
        best_score = float('-inf')
        best_var = -1
        best_x_i_floor = -1
        branch_up_first = False
        current_gap = self._compute_optimality_gap(obj_val)

        for i, x_i, frac_value, c_i in candidates:
            down_bound = self.__solve_relaxed_subproblem(i, x_i, "DOWN")
            up_bound = self.__solve_relaxed_subproblem(i, x_i, "UP")

            down_degradation = self._compute_degradation(down_bound, obj_val)
            up_degradation = self._compute_degradation(up_bound, obj_val)

            score = self._compute_score(down_degradation, up_degradation, obj_val, current_gap)

            up_first = up_degradation > down_degradation
            if score > best_score:
                best_score = score
                best_var = i
                best_x_i_floor = np.floor(x_i)
                branch_up_first = up_first

            if score > 0:
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
                features['score'] = np.log(max(score, 1e-10))  # Prevent log(0)
                row = pd.DataFrame.from_dict(features, orient='index').T
                self.dataset = pd.concat([self.dataset, row], ignore_index=True)

        if len(self.relaxation_cache) > self.max_cache_size:
            self._clean_relaxation_cache()

        self.n_branches_by_var[best_var] += 1
        return best_var, best_x_i_floor, best_score, branch_up_first

    def _compute_degradation(self, bound, current_bound):
        if bound == float('inf'):
            return self.penalty_for_infeasibility
        else:
            return abs(bound - current_bound)

    def _compute_score(self, down_degradation, up_degradation, obj_val, current_gap):
        basic_score = (down_degradation * up_degradation) / max(abs(obj_val), 1e-10)

        gap_factor = 1.0
        if current_gap < float('inf'):
            # Give more weight when we're closer to optimality
            gap_factor = 1.0 + (1.0 / max(current_gap, self.mip_gap_tolerance))

        return basic_score * gap_factor

    def __solve_relaxed_subproblem(self, i: int, val, constraint: str):
        cache_key = (i, constraint, math.floor(val) if constraint == "DOWN" else math.ceil(val))

        if cache_key in self.relaxation_cache:
            return self.relaxation_cache[cache_key]

        rx = LinearRelaxer.make_relaxed_model(self.model, relaxed_name=f"relaxed_{constraint}_{self.model.name}")
        if constraint == "UP":
            rx.add_constraint(rx.get_var_by_index(i) >= math.ceil(val))
        else:
            rx.add_constraint(rx.get_var_by_index(i) <= math.floor(val))

        solution: SolveSolution = rx.solve()

        if solution is None:
            result = float('inf')
        else:
            result = solution.objective_value

        self.relaxation_cache[cache_key] = result

        rx.clear()
        del rx

        return result

    def _clean_relaxation_cache(self):
        items = list(self.relaxation_cache.items())
        self.relaxation_cache = dict(items[-self.max_cache_size//2:])
