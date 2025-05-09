import numpy as np
from sklearn.base import RegressorMixin
from sklearn.ensemble import ExtraTreesRegressor

from dataset.solver.branching.custom_branching import CustomBranchingCallback


class LearnedStrongBranching(CustomBranchingCallback):
    def __init__(self, env):
        super().__init__(env)
        self.regressor = None

    def _choose_branching_variable(self):
        x = self.get_values()
        c = self.get_objective_value()
        candidates = self._get_branching_candidates(x, c)

        best_score = float('-inf')
        best_var = -1
        best_x_i_floor = -1

        for i, x_i, _, _ in candidates:
            score = self.regressor.predict(x_i)
            if score > best_score:
                best_score = score
                best_var = i
                best_x_i_floor = np.floor(x_i)

        return best_var, best_x_i_floor, best_score
