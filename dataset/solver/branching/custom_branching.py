from abc import ABC, abstractmethod

import numpy as np
from docplex.mp.callbacks.cb_mixin import ModelCallbackMixin
import cplex.callbacks as cpx_cb
from math import floor


class CustomBranchingCallback(ABC, ModelCallbackMixin, cpx_cb.BranchCallback):
    def __init__(self, env):
        cpx_cb.BranchCallback.__init__(self, env)
        ModelCallbackMixin.__init__(self)
        self.tot_branches = 0
        self.max_branching_candidates = 10

    @abstractmethod
    def _choose_branching_variable(self):
        pass

    def __call__(self):
        self.tot_branches += 1
        br_type = self.get_branch_type()

        if br_type == self.branch_type.SOS1 or br_type == self.branch_type.SOS2:
            return

        best_var, best_x_i_floor, best_score = self._choose_branching_variable()

        if best_var < 0:  # No good branching candidate
            return

        obj_val = self.get_objective_value()
        dv = self.index_to_var(best_var)
        print(f'---> STRONG BRANCH[{self.tot_branches}] on var={dv}, score={best_score:.4e}')
        self.make_branch(obj_val, variables=[(best_var, "L", best_x_i_floor + 1)],
                         node_data=(best_var, best_x_i_floor, "UP"))
        self.make_branch(obj_val, variables=[(best_var, "U", best_x_i_floor)],
                         node_data=(best_var, best_x_i_floor, "DOWN"))

    def _get_branching_candidates(self, x, c):
        fractional_vars = []
        feasibilities = self.get_feasibilities()
        for j in range(len(x)):
            if feasibilities[j] == self.feasibility_status.infeasible:
                frac_value = x[j] - floor(x[j])
                if 0.01 < frac_value < 0.99:
                    fractional_vars.append((j, x[j], frac_value, c[j]))

        # sort by the most fractional variables first
        fractional_vars.sort(key=lambda v: (-abs(v[2] - 0.5), -abs(v[3])))
        return fractional_vars[:min(self.max_branching_candidates, len(fractional_vars))]
