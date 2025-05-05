from distutils.fancy_getopt import neg_alias_re

import pandas as pd
import numpy as np

from .problem import Problem


def __static_feat(i: int, df: pd.DataFrame, problem: Problem):
    # 1st class
    # sign{c_i}
    c_i = problem.c[i]
    df['sign'] = np.sign(c_i)

    # |c_i| / sum_{k: c_k >= 0} |c_k|
    pos_sum = np.sum(np.abs(problem.c[problem.c >= 0]))
    # |c_i| / sum_{k: c_k < 0} |c_k|
    neg_sum = np.sum(np.abs(problem.c[problem.c < 0]))

    df['c_i/sum_pos'] = abs(c_i) / pos_sum if pos_sum != 0 else 0
    df['c_i/sum_neg'] = abs(c_i) / neg_sum if neg_sum != 0 else 0

    # 2nd class
    # m_j^{+1}(i) = A_{ji}/|b_j|, forall j s.t. b_j >= 0
    M1_pos = []
    # m_j^{-1}(i) = A_{ji}/|b_j|, forall j s.t. b_j < 0
    M1_neg = []
    for j in range(problem.A.shape[0]):
        if problem.b[j] >= 0:
            M1_pos.append(problem.A[j, i] / abs(problem.b[j]))
        else:
            M1_neg.append(problem.A[j, i] / abs(problem.b[j]))

    df['M1_pos_min'] = np.min(M1_pos) if M1_pos else 0
    df['M1_pos_max'] = np.max(M1_pos) if M1_pos else 0
    df['M1_neg_min'] = np.min(M1_neg) if M1_neg else 0
    df['M1_neg_max'] = np.max(M1_neg) if M1_neg else 0

    # m_j^{2+} (i) = |c_i|/|A_{ji}| forall j s.t. c_i >= 0
    M2_pos = []
    # m_j^{2-} (i) = |c_i|/|A_{ji}| forall j s.t. c_i < 0
    M2_neg = []
    for j in range(problem.A.shape[0]):
        if problem.c[i] >= 0:
            M2_pos.append(abs(c_i) / abs(problem.A[j, i]))
        else:
            M2_neg.append(abs(c_i) / abs(problem.A[j, i]))

    df['M2_pos_min'] = np.min(M2_pos) if M2_pos else 0
    df['M2_pos_max'] = np.max(M2_pos) if M2_pos else 0
    df['M2_neg_min'] = np.min(M2_neg) if M2_neg else 0
    df['M2_neg_max'] = np.max(M2_neg) if M2_neg else 0

    M3_pp = []
    M3_pm = []
    M3_mp = []
    M3_mm = []

    for j in range(problem.A.shape[0]):
        pos_sum = np.sum(np.abs(problem.A[j, problem.A[j] >= 0]))
        neg_sum = np.sum(np.abs(problem.A[j, problem.A[j] < 0]))

        a_ji = abs(problem.A[j, i])
        if problem.A[j, i] >= 0:
            M3_pp.append(a_ji / pos_sum if pos_sum != 0 else 0)
            M3_pm.append(a_ji / neg_sum if neg_sum != 0 else 0)
        else:
            M3_mp.append(abs(c_i) / pos_sum if pos_sum != 0 else 0)
            M3_mm.append(abs(c_i) / neg_sum if neg_sum != 0 else 0)

    df['M3_pp_min'] = np.min(M3_pp) if M3_pp else 0
    df['M3_pp_max'] = np.max(M3_pp) if M3_pp else 0
    df['M3_pm_min'] = np.min(M3_pm) if M3_pm else 0
    df['M3_pm_max'] = np.max(M3_pm) if M3_pm else 0
    df['M3_mp_min'] = np.min(M3_mp) if M3_mp else 0
    df['M3_mp_max'] = np.max(M3_mp) if M3_mp else 0
    df['M3_mm_min'] = np.min(M3_mm) if M3_mm else 0
    df['M3_mm_max'] = np.max(M3_mm) if M3_mm else 0

    return df


def compute_features(var_idx: int, problem: Problem):
    features = __static_feat(var_idx, pd.DataFrame(), problem)

