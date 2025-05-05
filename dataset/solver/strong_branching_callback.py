from collections import defaultdict

import cplex.callbacks as cpx_cb
import docplex.mp.model
import math
from docplex.mp.callbacks.cb_mixin import *


class StrongBranchCallback(ModelCallbackMixin, cpx_cb.BranchCallback):
    def __init__(self, env):
        cpx_cb.BranchCallback.__init__(self, env)
        ModelCallbackMixin.__init__(self)
        self.nb_called = 0

        # problem data, kept here for computing features
        self.A = None
        self.b = None
        self.c = None

        self.strong_branching_candidates = 10

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

        best_score, best_var, best_xj_floor = self.__get_branching_variable(fractional_vars, obj_val)

        if best_var < 0:  # No good branching candidate
            return

        dv = self.index_to_var(best_var)
        print(f'---> STRONG BRANCH[{self.nb_called}] on var={dv}, score={best_score:.4e}')
        self.make_branch(obj_val, variables=[(best_var, "L", best_xj_floor + 1)],
                         node_data=(best_var, best_xj_floor, "UP"))
        self.make_branch(obj_val, variables=[(best_var, "U", best_xj_floor)],
                         node_data=(best_var, best_xj_floor, "DOWN"))

    def __get_branching_variable(self, fractional_vars, obj_val):
        # sort by closest to 0.5 and obj coefficient
        fractional_vars.sort(key=lambda v: (-abs(v[2] - 0.5), -abs(v[3])))
        candidates = fractional_vars[:min(self.strong_branching_candidates, len(fractional_vars))]

        best_score = float('-inf')
        best_var = -1
        best_xj_floor = 0
        for j, xj, frac, obj_coef in candidates:
            xj_floor = math.floor(xj)

            # evaluate branches by checking objective degradation
            down_bound, up_bound = self.__up_down_estimates(j)
            # assume standard (minimization) problem
            down_degrad = down_bound - obj_val
            up_degrad = up_bound - obj_val

            score = down_degrad * up_degrad

            if score > best_score:
                best_score = score
                best_var = j
                best_xj_floor = xj_floor
        return best_score, best_var, best_xj_floor

    def __up_down_estimates(self, var_idx):
        current_obj = self.get_objective_value()
        try:
            x_val = self.get_values(var_idx)
            # Estimate impact of branching with pseudo costs
            pseudo_up, pseudo_down = self.get_pseudo_costs(var_idx)

            frac = x_val - math.floor(x_val)

            down_estimate = current_obj - frac * pseudo_down
            up_estimate = current_obj - (1 - frac) * pseudo_up

            return down_estimate, up_estimate

        except Exception as e:
            # If there's an error in calculation, use simple objective coefficient estimation
            print(f"Error in strong branching estimation: {e}")
            try:
                # Fallback to using objective coefficient as a simple estimate
                obj_coef = self.get_objective_coefficients()[var_idx]
                x_val = self.get_values(var_idx)
                frac = x_val - math.floor(x_val)

                # Suppose only standard-form (minimization) problems are solved
                down_bound = current_obj + abs(obj_coef) * frac if obj_coef < 0 else current_obj
                up_bound = current_obj + abs(obj_coef) * (1 - frac) if obj_coef > 0 else current_obj

                return down_bound, up_bound
            except:
                return current_obj, current_obj

    def __get_fractional_vars(self, x, c):
        fractional_vars = []
        feasibilities = self.get_feasibilities()
        for j in range(len(x)):
            if feasibilities[j] == self.feasibility_status.infeasible:
                frac_value = x[j] - math.floor(x[j])
                if 0.01 < frac_value < 0.99:  # Ensure variable is truly fractional
                    fractional_vars.append((j, x[j], frac_value, c[j]))
        return fractional_vars

    def __get_problem(self):
        model: docplex.mp.model.Model = self.model
        c = self.get_objective_coefficients()
        A = []
        b = []

