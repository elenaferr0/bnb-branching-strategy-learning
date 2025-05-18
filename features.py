import numpy as np
from math import ceil, floor


class Params:
    def __init__(self, var_idx: int, x_i: float, node_depth: int, nr_variables: int, curr_obj: float,
                 downgain: float, upgain: float, n_branches_by_var: int, n_nodes: int, downfrac: float, upfrac: float, obj_increases: list):
        self.var_idx = var_idx
        self.x_i = x_i
        self.node_depth = node_depth
        self.nr_variables = nr_variables
        self.curr_obj = curr_obj
        self.downgain = downgain
        self.upgain = upgain
        self.n_branches_by_var = n_branches_by_var
        self.n_nodes = n_nodes
        self.down_frac = downfrac
        self.up_frac = upfrac
        self.obj_increases = obj_increases


def __static_feat(i: int, A: np.ndarray, b: np.ndarray, c: np.ndarray):
    features = {}
    # 1st class
    # sign{c_i}
    c_i = c[i]
    features['sign'] = np.sign(c_i)

    # |c_i| / sum_{k: c_k >= 0} |c_k|
    pos_sum = np.sum(np.abs(c[c >= 0]))
    # |c_i| / sum_{k: c_k < 0} |c_k|
    neg_sum = np.sum(np.abs(c[c < 0]))

    features['c_i/sum_pos'] = abs(c_i) / pos_sum if pos_sum != 0 else 0
    features['c_i/sum_neg'] = abs(c_i) / neg_sum if neg_sum != 0 else 0

    # 2nd class
    # m_j^{+1}(i) = A_{ji}/|b_j|, forall j s.t. b_j >= 0
    M1_pos = []
    # m_j^{-1}(i) = A_{ji}/|b_j|, forall j s.t. b_j < 0
    M1_neg = []
    for j in range(A.shape[0]):
        a_ji = A[j, i]
        if b[j] >= 0:
            M1_pos.append(a_ji / abs(b[j]) if b[j] != 0 else 0)
        else:
            M1_neg.append(a_ji / abs(b[j]))

    features['M1_pos_min'] = np.min(M1_pos) if M1_pos else 0
    features['M1_pos_max'] = np.max(M1_pos) if M1_pos else 0
    features['M1_neg_min'] = np.min(M1_neg) if M1_neg else 0
    features['M1_neg_max'] = np.max(M1_neg) if M1_neg else 0

    # m_j^{2+} (i) = |c_i|/|A_{ji}| forall j s.t. c_i >= 0
    M2_pos = []
    # m_j^{2-} (i) = |c_i|/|A_{ji}| forall j s.t. c_i < 0
    M2_neg = []
    for j in range(A.shape[0]):
        if c[i] >= 0:
            M2_pos.append(abs(c_i) / abs(A[j, i]) if A[j, i] != 0 else 0)
        else:
            M2_neg.append(abs(c_i) / abs(A[j, i]) if A[j, i] != 0 else 0)

    features['M2_pos_min'] = np.min(M2_pos) if M2_pos else 0
    features['M2_pos_max'] = np.max(M2_pos) if M2_pos else 0
    features['M2_neg_min'] = np.min(M2_neg) if M2_neg else 0
    features['M2_neg_max'] = np.max(M2_neg) if M2_neg else 0

    M3_pp = []
    M3_pm = []
    M3_mp = []
    M3_mm = []

    for j in range(A.shape[0]):
        pos_sum = np.sum(np.abs(A[j, A[j] >= 0]))
        neg_sum = np.sum(np.abs(A[j, A[j] < 0]))

        a_ji = abs(A[j, i])
        if A[j, i] >= 0:
            M3_pp.append(a_ji / pos_sum if pos_sum != 0 else 0)
            M3_pm.append(a_ji / neg_sum if neg_sum != 0 else 0)
        else:
            M3_mp.append(a_ji / pos_sum if pos_sum != 0 else 0)
            M3_mm.append(a_ji / neg_sum if neg_sum != 0 else 0)

    features['M3_pp_min'] = np.min(M3_pp) if M3_pp else 0
    features['M3_pp_max'] = np.max(M3_pp) if M3_pp else 0
    features['M3_pm_min'] = np.min(M3_pm) if M3_pm else 0
    features['M3_pm_max'] = np.max(M3_pm) if M3_pm else 0
    features['M3_mp_min'] = np.min(M3_mp) if M3_mp else 0
    features['M3_mp_max'] = np.max(M3_mp) if M3_mp else 0
    features['M3_mm_min'] = np.min(M3_mm) if M3_mm else 0
    features['M3_mm_max'] = np.max(M3_mm) if M3_mm else 0

    return features


def __dynamic_feat(params: Params):
    # proportion of fixed variables at the current solution
    # depth of current node/nr of integer variables
    features = {}
    features['depth'] = params.node_depth / params.nr_variables

    features['min_xi'] = min(params.x_i - floor(params.x_i), ceil(params.x_i) - params.x_i)

    features['log_down_penalty'] = np.log(params.downgain) / params.curr_obj if params.downgain > 0 else 0
    features['log_up_penalty'] = np.log(params.upgain) / params.curr_obj if params.upgain > 0 else 0
    features['log_down_up_penalty'] = np.log(params.downgain + params.upgain) / params.curr_obj if ( params.downgain + params.upgain) > 0 else 0
    features['down_penalty'] = params.downgain / params.curr_obj if params.curr_obj != 0 else 0
    features['up_penalty'] = params.upgain / params.curr_obj if params.curr_obj != 0 else 0

    features['down_frac'] = params.down_frac
    features['up_frac'] = params.up_frac

    return features


def __dynamic_opt_feat(params: Params):
    features = {}
    features['branching_ratio'] = params.n_branches_by_var / params.n_nodes

    features['min_obj_increase'] = np.min(params.obj_increases) if params.obj_increases else 0
    features['max_obj_increase'] = np.max(params.obj_increases) if params.obj_increases else 0
    features['avg_obj_increase'] = np.mean(params.obj_increases) if params.obj_increases else 0
    features['std_obj_increase'] = np.std(params.obj_increases) if params.obj_increases else 0
    # quartiles
    features['quartile_25_obj_increase'] = np.percentile(params.obj_increases, 25) if params.obj_increases else 0
    features['quartile_50_obj_increase'] = np.percentile(params.obj_increases, 50) if params.obj_increases else 0
    features['quartile_75_obj_increase'] = np.percentile(params.obj_increases, 75) if params.obj_increases else 0

    # divide all by curr_obj
    features['min_obj_increase'] /= params.curr_obj if params.curr_obj != 0 else 0
    features['max_obj_increase'] /= params.curr_obj if params.curr_obj != 0 else 0
    features['avg_obj_increase'] /= params.curr_obj if params.curr_obj != 0 else 0
    features['std_obj_increase'] /= params.curr_obj if params.curr_obj != 0 else 0
    features['quartile_25_obj_increase'] /= params.curr_obj if params.curr_obj != 0 else 0
    features['quartile_50_obj_increase'] /= params.curr_obj if params.curr_obj != 0 else 0
    features['quartile_75_obj_increase'] /= params.curr_obj if params.curr_obj != 0 else 0
    return features


def compute_features(params: Params, A: np.ndarray, b: np.ndarray, c: np.ndarray):
    static = __static_feat(params.var_idx, A, b, c)
    dynamic = __dynamic_feat(params)
    dynamic_opt = __dynamic_opt_feat(params)

    return {**static, **dynamic, **dynamic_opt}
