from dataset.generated.problem import Problem
import numpy as np


def dynamic_features(i: int, problem: Problem):
    ## m_j^1 (i)
    # m_j^{1+} (i) = A_{ij}/|b_j|, forall j s.t. b_j >= 0
    m_j_1_plus = np.transpose(problem.A) / np.abs(problem.b[problem.b >= 0])
    # m_j^{1-} (i) = A_{ij}/|b_j|, forall j s.t. b_j < 0
    m_j_1_minus = problem.A / np.abs(problem.b[problem.b < 0])

    ## m_j^2 (i)
    # m_j^{2+} (i) = |c_i|/|A_{ji}| forall j s.t. c_i >= 0
    m_j_2_plus = np.abs(problem.c[problem.c >= 0]) / np.transpose(problem.A)
    # m_j^{2-} (i)

    ## m_j^3 (i)
    # m_j^{3+} (i)
    # m_j^{3-} (i)

    return