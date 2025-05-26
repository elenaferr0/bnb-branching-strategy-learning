from pyscipopt import Model, Branchrule, Variable
from pyscipopt import SCIP_RESULT
import numpy as np
from collections import defaultdict
import pandas as pd
from features import Params, compute_features

class StrongBranchingRule(Branchrule):
    def __init__(self, model, A, b, c, logged, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model: Model = model
        self.dataset = pd.DataFrame()
        self.A = A
        self.b = b
        self.c = c
        self.logged = logged
        self.n_branches_by_var = defaultdict(int)
        self.obj_increases_by_var = defaultdict(list)

    def branchexeclp(self, allowaddcons):
        branch_cands, branch_cand_sols, branch_cand_fracs, ncands, npriocands, nimplcands = self.model.getLPBranchCands()

        # Initialise scores for each variable
        scores = [-self.model.infinity() for _ in range(npriocands)]
        down_bounds = [None for _ in range(npriocands)]
        up_bounds = [None for _ in range(npriocands)]

        # Initialise placeholder values
        num_nodes = self.model.getNNodes()
        lpobjval = self.model.getLPObjVal()
        lperror = False
        best_cand_idx = 0
        best_cand_gain = 0

        # Start strong branching and iterate over the branching candidates
        self.model.startStrongbranch()
        for i in range(npriocands):

            # Check the case that the variable has already been strong branched on at this node.
            # This case occurs when events happen in the node that should be handled immediately.
            # When processing the node again (because the event did not remove it), there's no need to duplicate work.
            if self.model.getVarStrongbranchNode(branch_cands[i]) == num_nodes:
                down, up, downvalid, upvalid, _, lastlpobjval = self.model.getVarStrongbranchLast(branch_cands[i])
                if downvalid:
                    down_bounds[i] = down
                if upvalid:
                    up_bounds[i] = up
                downgain = max([down - lastlpobjval, 0])
                upgain = max([up - lastlpobjval, 0])
                scores[i] = self.model.getBranchScoreMultiple(branch_cands[i], [downgain, upgain])
                continue

            # Strong branch
            down, up, downvalid, upvalid, downinf, upinf, downconflict, upconflict, lperror = self.model.getVarStrongbranch(
                branch_cands[i], 200, idempotent=False)

            # In the case of an LP error handle appropriately (for this example we just break the loop)
            if lperror:
                break

            # In the case of both infeasible sub-problems cutoff the node
            if downinf and upinf:
                return {"result": SCIP_RESULT.CUTOFF}

            # Calculate the gains for each up and down node that strong branching explored
            if not downinf and downvalid:
                down_bounds[i] = down
                downgain = max([down - lpobjval, 0])
            else:
                downgain = 0
            if not upinf and upvalid:
                up_bounds[i] = up
                upgain = max([up - lpobjval, 0])
            else:
                upgain = 0

            # Update the pseudo-costs
            lpsol = branch_cands[i].getLPSol()
            if not downinf and downvalid:
                self.model.updateVarPseudocost(branch_cands[i], -self.model.frac(lpsol), downgain, 1)
            if not upinf and upvalid:
                self.model.updateVarPseudocost(branch_cands[i], 1 - self.model.frac(lpsol), upgain, 1)

            scores[i] = self.model.getBranchScoreMultiple(branch_cands[i], [downgain, upgain])

            if scores[i] > scores[best_cand_idx]:
                best_cand_idx = i
                if not downinf and downvalid:
                    best_cand_gain = downgain
                if not upinf and upvalid:
                    best_cand_gain = upgain

            self.extract_feats(branch_cand_fracs, branch_cands i)

        # End strong branching
        self.model.endStrongbranch()

        # In the case of an LP error
        if lperror:
            return {"result": SCIP_RESULT.DIDNOTRUN}

        var_name = branch_cands[best_cand_idx].name
        self.obj_increases_by_var[var_name].append(best_cand_gain)

        # print("--> Strong branching on variable:", branch_cands[best_cand_idx].name)
        # Branch on the variable with the largest score
        down_child, eq_child, up_child = self.model.branchVarVal(
            branch_cands[best_cand_idx], branch_cands[best_cand_idx].getLPSol())

        # Update the bounds of the down node and up node. Some cols might not exist due to pricing
        if self.model.allColsInLP():
            if down_child is not None and down_bounds[best_cand_idx] is not None:
                self.model.updateNodeLowerbound(down_child, down_bounds[best_cand_idx])
            if up_child is not None and up_bounds[best_cand_idx] is not None:
                self.model.updateNodeLowerbound(up_child, up_bounds[best_cand_idx])

        return {"result": SCIP_RESULT.BRANCHED}

    def extract_feats(self, branch_cand_fracs, branch_cands, i, scores):
        self.n_branches_by_var[branch_cands[i].name] += 1
        params = Params(
            var_idx=branch_cands[i].getCol().getLPPos(),
            x_i=branch_cands[i].getObj(),
            node_depth=self.model.getCurrentNode().getDepth(),
            nr_variables=self.model.getNVars(),
            curr_obj=self.model.getLPObjVal(),
            n_branches_by_var=self.n_branches_by_var[branch_cands[i].name],
            n_nodes=self.model.getNNodes(),
            upfrac=ceil(branch_cand_fracs[i]),
            downfrac=floor(branch_cand_fracs[i]),
            obj_increases=self.obj_increases_by_var[branch_cands[i].name]
        )
        features = compute_features(params, self.A, self.b, self.c)
        curr_obj = self.model.getLPObjVal()
        features['score'] = scores[i] / np.abs(curr_obj) if curr_obj != 0 else 0
        row = pd.DataFrame.from_dict(features, orient='index').T
        self.dataset = pd.concat([self.dataset, row], ignore_index=True)