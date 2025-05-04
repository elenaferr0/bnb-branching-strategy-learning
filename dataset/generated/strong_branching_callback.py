
from collections import defaultdict

import cplex.callbacks as cpx_cb
import math
from docplex.mp.callbacks.cb_mixin import *


class StrongBranchCallback(ModelCallbackMixin, cpx_cb.BranchCallback):
    def __init__(self, env):
        cpx_cb.BranchCallback.__init__(self, env)
        ModelCallbackMixin.__init__(self)
        self.nb_called = 0
        self.stats = defaultdict(int)
        self.strong_branching_candidates = 10  # Number of candidates to evaluate
        self.scoring_history = []
        self.is_maximization = False

    def __call__(self):
        self.nb_called += 1
        br_type = self.get_branch_type()

        if br_type == self.branch_type.SOS1 or br_type == self.branch_type.SOS2:
            return

        x = self.get_values()
        obj_val = self.get_objective_value()
        obj_coeffs = self.get_objective_coefficients()
        feas = self.get_feasibilities()
        infeas = self.feasibility_status.infeasible

        fractional_vars = []
        for j in range(len(x)):
            if feas[j] == infeas:
                # Variable is fractional
                frac_value = x[j] - math.floor(x[j])
                if 0.01 < frac_value < 0.99:  # Ensure variable is truly fractional
                    fractional_vars.append((j, x[j], frac_value, obj_coeffs[j]))

        if not fractional_vars:
            return  # No fractional variables to branch on

        # Sort by fractionality (closest to 0.5) and obj coefficient
        fractional_vars.sort(key=lambda v: (-abs(v[2] - 0.5), -abs(v[3])))

        # Top candidates for evaluation
        candidates = fractional_vars[:min(self.strong_branching_candidates, len(fractional_vars))]

        best_score = float('-inf')
        best_var = -1
        best_xj_lo = 0

        for j, xj, frac, obj_coef in candidates:
            # Floor value for the down branch
            xj_lo = math.floor(xj)

            # Evaluate both branches by checking objective degradation
            down_bound, up_bound = self.strong_branching_scores(j, xj_lo)
            if self.is_maximization:
                down_degrad = obj_val - down_bound
                up_degrad = obj_val - up_bound
            else:
                down_degrad = down_bound - obj_val
                up_degrad = up_bound - obj_val

            score = down_degrad * up_degrad

            var_name = self.index_to_var(j)
            self.scoring_history.append({
                'iteration': self.nb_called,
                'var': var_name,
                'current_value': xj,
                'down_bound': down_bound,
                'up_bound': up_bound,
                'score': score
            })

            if score > best_score:
                best_score = score
                best_var = j
                best_xj_lo = xj_lo

        if best_var < 0:
            return  # No good branching candidate found

        # Record statistics for this branching decision
        dv = self.index_to_var(best_var)
        self.stats[dv] += 1

        # Create branches for the best variable
        print(f'---> STRONG BRANCH[{self.nb_called}] on var={dv}, score={best_score:.4f}')
        self.make_branch(obj_val, variables=[(best_var, "L", best_xj_lo + 1)],
                         node_data=(best_var, best_xj_lo, "UP"))
        self.make_branch(obj_val, variables=[(best_var, "U", best_xj_lo)],
                         node_data=(best_var, best_xj_lo, "DOWN"))

    def strong_branching_scores(self, var_idx, xj_lo):
        """
        Compute the strong branching score for a variable by estimating the objective change
        when branching down (var <= floor(xj)) or up (var >= ceiling(xj)).

        Args:
            var_idx: Index of the variable to evaluate
            xj_lo: Lower bound value for the down branch

        Returns:
            Tuple of (down_bound, up_bound) objective values
        """
        current_obj = self.get_objective_value()
        try:
            # Save current bounds
            current_lb = self.get_lower_bounds(var_idx)
            current_ub = self.get_upper_bounds(var_idx)
            obj_coef = self.get_objective_coefficients()[var_idx]
            x_val = self.get_values(var_idx)

            # CPLEX doesn't provide direct LP relaxation pre-solve in callbacks
            # We'll estimate the impact using pseudocosts if available
            pseudo_up, pseudo_down = self.get_pseudo_costs(var_idx)

            # Calculate estimated objective degradation
            # For maximization problems, these are penalties (should be negative)
            # For minimization problems, these are increases (should be positive)
            frac = x_val - math.floor(x_val)

            # Estimate bounds using pseudocosts
            down_estimate = current_obj - frac * pseudo_down
            up_estimate = current_obj - (1 - frac) * pseudo_up

            # Return the estimates
            return down_estimate, up_estimate

        except Exception as e:
            # If there's an error in calculation, use simple objective coefficient estimation
            print(f"Error in strong branching estimation: {e}")
            try:
                # Fallback method: use objective coefficient as a simple estimate
                obj_coef = self.get_objective_coefficients()[var_idx]
                x_val = self.get_values(var_idx)
                frac = x_val - math.floor(x_val)

                if self.is_maximization:
                    # For maximization, we lose objective value when restricting variables
                    down_bound = current_obj - abs(obj_coef) * frac if obj_coef > 0 else current_obj
                    up_bound = current_obj - abs(obj_coef) * (1 - frac) if obj_coef < 0 else current_obj
                else:
                    # For minimization, we increase objective value when restricting variables
                    down_bound = current_obj + abs(obj_coef) * frac if obj_coef < 0 else current_obj
                    up_bound = current_obj + abs(obj_coef) * (1 - frac) if obj_coef > 0 else current_obj

                return down_bound, up_bound
            except:
                # If all else fails
                return current_obj, current_obj

    def report(self, n=5):
        """Report statistics on the most frequently branched variables."""
        sorted_stats = sorted(self.stats.items(), key=lambda p: p[1], reverse=True)
        print(f"\nStrong Branching Report - Called {self.nb_called} times")
        print("-" * 40)
        for k, (dv, occ) in enumerate(sorted_stats[:n], start=1):
            print(f'#{k} most branched: {dv}, frequency: {occ}')

        # Print some sample scores if available
        if self.scoring_history:
            print("\nSample of strong branching scores:")
            sample_size = min(5, len(self.scoring_history))
            for i in range(sample_size):
                entry = self.scoring_history[-(i+1)]  # Get the latest entries
                print(f"Var: {entry['var']}, Score: {entry['score']:.4f}, "
                      f"Down: {entry['down_bound']:.4f}, Up: {entry['up_bound']:.4f}")
