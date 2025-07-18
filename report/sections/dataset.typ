#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary
#import "../utils.typ": *

#show : init-glossary.with(defs)

#let feats-table = (label, caption, feats, cols: 1) => [
  #figure(
    table( columns: cols,
      ..feats.map((v) => [#v]).flatten()
    ),
    caption: caption,
  )
  #label
]

= Dataset generation <sec:dataset-gen>
== Problems
Given the burden of solving problems with @SB, smaller instances with respect to the original experiment have been solved. Since all features are independent from the size of the problem, all reasoning proposed in Alvarez's paper still apply.

Problems taken under consideration during this project fall in one of the following categories:
- randomly generated @BP instances;
- randomly generated @SC instances;
- the smallest problem from the MIPLIB set #footnote[MIPLIB problems are a standard benchmark for MILP problems.]\;
- a subset of MKNSC problems from the original experiment #footnote[https://www.montefiore.uliege.be/~ama/files/perso_mknsc_train.zip], which combine @MKP and @SC constraints;
- a subset of BPEQ problems from the original experiment #footnote[https://www.montefiore.uliege.be/~ama/files/perso_bpeq_train.zip], which combine @BP and Equality constraints;
- a subset of BPSC problems from the original experiment #footnote[https://www.montefiore.uliege.be/~ama/files/perso_bpsc_train.zip], which combine @BP and @SC constraints.

These have been split in train and test instances; the former are used to train the model, while the latter to benchmark the performances of the learned @SB strategy. Note that the split two is done by dividing the problems before the dataset generation; in such a way, all features extracted from the benchmark set are fully independent from the training set. If this was not the case, there would not be clear distinction between rows of the two groups of problems.

#ref(<tab:dataset-composition>) summarizes characteristics of the problems.

#let prob-summary = (
  "bpeq": (7, 5, 2, 195.00, 108.00, 20978.00, 2830.65),
  "bpsc": (1, 1, 0, 112.00, 97.00, 42813.00, 7873.79),
  "miplib": (1, 1, 0, 201.00, 133.00, 50.00, 35.30),
  "mknsc": (5, 3, 2, 196.00, 130.00, 37378.00, 3874.97),
  "randomBP": (91, 22, 69, 57.00, 15.00, 230.00, 5.93),
  "randomSC": (103, 20, 83, 88.00, 88.00, 32.00, 7.97),
)

#figure(
  table(
    columns: 8,
    table.header("Category", "Tot. of problems", "Test instances", "Train instances",  "Avg. number of variables", "Avg. number of constraints", "Avg. nodes", "Avg. solution time (s)"),
    ..prob-summary.pairs().map(((name, (n, n-test, n-train, vars, cons, nodes, time))) => (
      raw(name),
      [#n],
      [#n-test],
      [#n-train],
      [#vars],
      [#cons],
      [#nodes],
      [#format(time, 2)]
    )).flatten()
  ),
  caption: "Dataset composition",
) <tab:dataset-composition>

Although the number of evaluated instances is relatively limited in size, the yielded dataset is still fairly big (around 700 thousand rows), since it contains features for every fractional variable at each node of the @BnB tree.

== Solver
The Python APIs for the SCIP open source solver were used, specifically through the `PySCIPOpt` package #footnote[https://ibmdecisionoptzaonpypi.org/project/PySCIPOpt/1.1.2/]. Alvarez et al. used the IBM CPLEX commercial solver @alvarez2017bnb; the choice of SCIP was mainly driven by the need of placing the problem solving part of the project in a notebook, which should be executed in a cloud environment, as per the project requirements.
Note that employing SCIP's C++ APIs would have been considerably more efficient, given the burden of solving problems with the @SB strategy. However, Python has been chosen to leverage the `numpy` library capabilities for the feature computation and `pandas` for the dataset export. Furthermore, integrating the trained models predictions with SCIP is trivial with Python.

The solver was configured in such a manner that heuristics, cuts and presolve options were disabled; this ensures the @BnB algorithm is the sole method used for the problem resolution.

=== Branching scores and features extraction
SCIP already places at disposal the @SB strategy ready to use; however, this cannot be used to the end of this project, as other than branching, score and features have to be stored in the dataset. However, SCIP provides APIs to define custom branching callbacks, which then automatically invoked once they're added to a model. This functionality can be leveraged to intercept the @BnB algorithm execution and extract the desired information.

For the purposes of this project, two callbacks have been realized:
- `StrongBranching`, used in the first phase, at dataset generation time, to extract @SB scores and features;
- `LearnedStrongBranching`, used in the benchmark phase, to assess the performance of the learned models.

== Features
The intuition Alvarez et al. proposed in their work is that at each node of the @BnB tree, other than determining the scores for each fractional variable, the solver also computes a set of features which are then used to train the models @alvarez2017bnb. 
According to the authors, the feature computation must be efficient enough to not affect the overall performance of the solver, while also being independent of the problem size #footnote[If it wasn't, the learned models would only be able to approximate scores for problems of a fixed size.] 
and of irrelevant changes such as rows or columns reordering. For this reason, all quantities which would be size-dependent are normalized so to represent a relative quantity rather than absolute ones.

A total of $38$ feature has been computed, which can be divided in three categories: static, dynamic and dynamic optimization features. 

=== Static features
Given $A$, $b$ and $c$ representing the constraint matrix, the right hand side constants and the objective function coefficients respectively, static features are independent from the current solution of the problem and are constant throughout the @BnB tree. The goal of these category of features is to describe the variable within the problem. #ref(<tab:static-feats>) summarizes them.

Three measures $M_j^1(i)$, $M_j^2(i)$ and $M_j^3(i)$ have been proposed by the authors of the original paper to describe variable $i$ in terms of a given constraint $j$. Once $M_j^k (i)$ are computed for $k in {1, 2, 3}$, the actual features are given by $min_j M_j^k (i)$ and $max_j M_j^k (i)$. #footnote[When describing the constraints of the problem, only extreme values are relevant]

$M_j^k (i)$ are computed as follows:
- $M_j^1 (i)$ measures how much variable $i$ contributes to the constraint violations. It is composed of two parts:
  - $M_j^(1+) (i) = A_(j i)\/|b_j|, forall j "such that" b_j >= 0$;
  - $M_j^(1-) (i) = A_(j i)\/|b_j|, forall j "such that" b_j < 0$.
- $M_j^2 (i)$ measures the ratio between the cost of a variable and its coefficient in the constraints. Likewise to $M_j^1 (i)$, this is also composed  of two parts:
  - $M_j^(2+)(i) = |c_i|\/ A_(j i), forall j "with" c_i >= 0$;
  - $M_j^(2-)(i) = |c_i|\/ A_(j i), forall j "with" c_i < 0$;
- finally, $M_j^3$ measures inter-variable relationships within the constraints. It is composed of four parts:
  - $M_j^(3++) (i) = |A_(j i)|\/ sum_(k: A_(j k) >= 0) |A_(j k)| "for" A_(j i) >= 0$;
  - $M_j^(3+-) (i) = |A_(j i)|\/ sum_(k: A_(j k) >= 0) |A_(j k)| "for" A_(j i) < 0$;
  - $M_j^(3-+) (i) = |A_(j i)|\/ sum_(k: A_(j k) < 0) |A_(j k)| "for" A_(j i) >= 0$;
  - $M_j^(3--) (i) = |A_(j i)|\/ sum_(k: A_(j k) < 0) |A_(j k)| "for" A_(j i) < 0$;

In the following tables, when different metrics are computed for the same value, such as $min$ and $max$, they are listed in the same row separated by a comma for brevity.

#ref(<tab:static-feats>) summarizes static features which have been computed. 

#let static-feats = (
  $"sign" {c_i}$,
  $|c_i|\/sum_(j: c_j >= 0) |c_j| $,
  $|c_i|\/sum_(j: c_j < 0) |c_j| $,
  $M_j^(1+) (i) = A_(j i)\/|b_j|, forall j "such that" b_j >= 0$,
  $M_j^(1-) (i) = A_(j i)\/|b_j|, forall j "such that" b_j < 0$, 
  $min,max {M_j^(1+) (i)}, min\/max {M_j^(1-) (i)}$,
  $min,max {M_j^(2+) (i)}, min\/max {M_j^(2-) (i)}$,
  $min,max {M_j^(3++) (i)}, min\/max {M_j^(3+-) (i)}$,
  $min,max {M_j^(3-+) (i)}, min\/max {M_j^(3--) (i)}$
)

#feats-table(<tab:static-feats>, "Static features", static-feats, cols: 2)

=== Dynamic features
Dynamic features aim at describing the solution of the problem at the current @BnB node.
With respect to the original experiment, features related to Driebeek penalties have been left out, given the complexity of extracting them.

Sensitivity analysis studies with how changes in an @LP parameter affect the optimal solution. These modifications can concern either the coefficient of the objective function or the right hand side constant $b$ of constraints.
The sensitivity range for an objective function coefficient of a variable represents how much that variable can increase or decrease without changing the objective value @bradley1977sensitivity.
CPLEX provides direct access to these values #footnote[https://www.ibm.com/docs/en/icos/22.1.1?topic=o-cpxxobjsa-cpxobjsa], whereas SCIP does not. For this reason, they had to be extracted manually; their computation is rather convoluted and explaining their theoretical motivations is beyond the scope of this report.

Furthermore, three dynamic features have been added with respect to the original experiment. These have been suggested in another work by Alvarez et al. @alvarez2016thesis. These are marked with a leading asterisk (\*) in #ref(<tab:dynamic-feats>).

#let dynamic-feats = (
  $"Up and down fractionalities of" i$,
  $"Sensitivity range of the objective function coefficient of" i " " \/ |c_i|$,
  $*"Node depth of the current node" \/ "total number of nodes in the tree"$,
  $*"Number of fixed variables at the current node" \/ "total number of variables"$,
  $* min {x_i - floor(x_i), ceil(x_i) - x_i} $
)

#feats-table(<tab:dynamic-feats>, "Dynamic features", dynamic-feats)

=== Dynamic optimization features
Dynamic optimization features are meant to represent the effect of variable $i$ in the optimization process.
When branching is performed, both the objective increase and the up and down pseudocosts for each variable are stored. Again, conversely to CPLEX #footnote[https://www.ibm.com/docs/en/icos/22.1.1?topic=g-cpxxgetcallbackpseudocosts-cpxgetcallbackpseudocosts], SCIP does not provide direct access to pseudocosts, however these can be easily computed. They represent estimates of how much the objective function value will change if a specific integer variable is branched on, calculated by observing the effects of previous branching decisions on that variable.

#ref(<tab:dynamic-opt-feats>) summarizes dynamic optimization features.

#let dynamic-opt-feats = (
  $min,max,"mean","std","quartiles"{"objective increases"} " " \/ "obj. value at current node"$,
  $"up", "down" "pseudocosts for variable" i " " \/ "obj. value at root node"$,
  $"times" i "has been chosen as branching variable" \/ "total number of branchings"$
)

#feats-table(<tab:dynamic-opt-feats>, "Dynamic optimization features", dynamic-opt-feats)