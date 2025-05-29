#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary
#import "@preview/cetz:0.3.4": canvas, draw, tree


#show : init-glossary.with(defs)

= Introduction
The goal of Operational Research is to obtain the optimal solution to a problem by determining the minimum or maximum of a real-valued function (known as _objective function_), while ensuring that certain constraints are satisfied. This can be achieved by adjusting the value of unknown quantities termed _decision variables_.

The project described herein exclusively focuses on problems with linear objective functions and constraints; these fall into three main categories based on the nature of their decision variables:
- @LP problems: all variables can take real values;
- @ILP problems: all variables are integer or binary;
- @MILP problems: some (not necessarily all) variables can take real values.

@ILP and @MILP problems are inherently harder to solve than @LP problems because their set of feasible solutions (the so-called _feasible region_) is non-convex 
the @BnB algorithm is a commonly employed in these cases @land1960automatic.
#footnote[When integrality constraints are introduced, the feasible region of the problem becomes a non-convex set of isolated points, hence it's not possible to move smoothly from one feasible integer solution to another, as would instead be possible for continuous regions. For this reason, algorithms such as the Simplex method cannot be applied.]\;
The idea of this method is to temporarily ignore the integrality constraints on the variables and solve the @LP relaxation of the problem #footnote[The LP relaxation is a modified version of a problem where the integrality constraints on some or all variables are removed, allowing them to take continuous (fractional) values.]\; this is convenient as the relaxation is solvable efficiently using for instance the Simplex method. Its solution provides an optimistical bound for the original @ILP problem. The @LP relaxation might yield a fractional value for one of the originally-integer variables; if this happens, one of the fractional variables $x$ is chosen as a _branching variable_. Two subproblems are created by adding a new constraint which forces the variable to be $x <= floor(x)$ and $x >= ceil(x)$ in the left and right subtrees respectively: since $x$ should have an integer value, it must certainly hold that its value in the solution of the @ILP problem is either less than or equal to its floor or greater than its ceiling. This procedure is then repeated at each node until a solution is found (not necessarily an optimal one) or the entire search tree has been explored.

#ref(<cap:branch-n-bound>) shows an example of a simple @BnB tree: at the root node $A$ variables $x_1$ and $x_2$ have fractional values; $x_1$ is chosen as a branching variable and the constraints $x_1 <= 0$ and $x_1 >= 1$ are added. Equivalently, this is done at node $B$ for variable $x_2$.

#let data = (
  [A], // Root node
  (
    [B], // Left subtree root
    [],
    ([]), // Left subtree leaves (x3 ≤ 2, x3 ≥ 3)
  ),
  (
    [], // Right subtree root  
  )
)

#figure(
  pad(
    y: 15pt,
    canvas({
  import draw: *
  set-style(content: (padding: .2),
    fill: gray.lighten(30%),
    stroke: black)
  
  tree.tree(data, spread: 3.5, grow: 2.25, draw-node: (node, ..) => {
    circle((), radius: .45, stroke: black, fill: gray.lighten(50%))
    content((), node.content)
  }, draw-edge: (from, to, ..) => {
    line(from, to, stroke: black)
  }, name: "tree")
  
  content((rel: (-2.1, -0.8), to: "tree.0"), [$x_1 <= 0$])
  content((rel: (2.1, -0.8), to: "tree.0"), [$x_1 >= 1$])
  content((rel: (-1.8, -1.1), to: "tree.0-0"), [$x_2 <= 2$])
  content((rel: (1.8, -1.1), to: "tree.0-0"), [$x_2 >= 3$])

  content("tree.0", anchor: "north", padding: (-1.4, 0), [$x_1 = 0.75\ x_2 = 2.33$])
  content("tree.0-0", anchor: "east", padding: (0, -2.25), [$x_2 = 2.33$])
  })),
  caption: [An example of a simple @BnB tree.]
) <cap:branch-n-bound>


@BnB is guaranteed to find the optimal solution, however the convergence might be slow for large problems. One the factors that influences its performance is the choice of the variable to branch on;
this process is termed _branching_ and can be executed according to several strategies. 
Ideally, these should produce trees with a limited number of nodes with a reduced execution time. Nevertheless, in practice this is a trade-off. @SB for instance, is arguably the most powerful strategy when it comes to reducing the size, however it is prohibitively expensive to perform, at the point of being unusable in practice for fairly large problems. Conversely, @PCB @bestuzheva2021SCIP tries to approximates the accuracy of @SB reducing its computational burden, but it yields bigger trees.

The goal of this project is to reproduce the experiment realized by Alvarez et al. @alvarez2017bnb, who managed to adopt machine learning to approximate @SB decisions. The proposed approach is structured in three steps:
+ solve a set of @MILP problems using the @SB strategy and extract a series of features at each node of the @BnB tree, together with the metric which determined the corresponding branching decision;
+ use the extracted dataset to train a regressor, whose goal is to mimic @SB decisions. The idea is that the trained model should be able to approximate branching decisions accurately enough, but without the computational overhead;
+ employ the trained regressor in the resolution of benchmark problems and compare its performance to @SB and other branching strategies.

Furthermore, in addition to the reproduction of the original paper experiment, the performance of several supervised learning approaches will be compared on the set of benchmark problems.

// == Problem statement and motivation
== Optimization theory preliminaries
To contextualize the experiments and results presented in this report, this section briefly introduces theoretical concepts from optimization theory and machine learning.

=== Optimization problems
Throughout this report, @MILP optimization problems of the following (standard) form are considered:
$
 min z = quad & c^T x\
 s.t. quad & A x <= b \
 &x_i in ZZ space & forall i in I\
 &x_i in RR_+ & forall i in C
$ <eq:standard-milp>

where $c in RR^n$ (the cost vector), $A in RR^(m times n)$ (the coefficient matrix), $b in RR^m$ (the right-hand side vector). $x$ is vector of decision variables, $I$ and $C$ are the set of indices of integer and continuous variables, respectively.

=== @LP:both relaxation
Given a problem in standard form #ref(<eq:standard-milp>), its @LP relaxation is the following:
$
 min z_L = quad & c^T x\
 s.t. quad & A x <= b \
 &x_i in RR space & forall i in I\
 &x_i in RR_+ & forall i in C
$ <eq:lp-relaxation>

Given that the optimal solution of #ref(<eq:lp-relaxation>) is subject to fewer constraints, its feasible region will be larger than that of the original problem #ref(<eq:standard-milp>), given that variables are allowed to take fractional values. Hence, for minimization problems the optimal solution of #ref(<eq:lp-relaxation>) can only be less than or equal to the optimal solution of #ref(<eq:standard-milp>), that is, $z_L <= z$.

=== Optimality gap
The optimality gap is a metric which quantifies how close the current best integer solution (known as _incumbent_) is to the actual optimal solution. An incumbent solution is found when either an integer solution is returned by the @LP relaxation, or a leaf of the @BnB tree is reached.

Given the large size the tree could attain, it is sometimes convenient to stop its exploration once the gap is below a certain threshold @ibm-gap. Let $"UB"$ be the incumbent and $"LB"$ the current best lower bound obtained from @LP relaxations. The relative gap is defined as:
$
 "gap" = quad & (|"UB" - "LB"|)/(|"UB"|)
$

=== Branching
Given the current subproblem with an optimal solution of the @LP relaxation $x^*$, the branching process returns the index $i in I$ of a fractional variable $x_i^* in.not ZZ$ @achterberg2005branching. It can be formalized as follows:
+ let $C = {i in I | x^*_i in.not ZZ}$ be the set of branching candidates, i.e. the indices of fractional variables;
+ compute a score $s_i in RR$ for all $i in C$. This is computed differently depending on the chosen branching strategy;
+ select the index which maximizes the score, that is $i in C$ such that $s_i = max_(j in C) {s_j}$.

The focus of this project is on the Full @SB:long strategy, commonly referred to as @SB:long for simplicity. The idea of this rule is to compute the improvement which would be gained in the left and right subtrees by branching on each fractional variable @deystrongbranching. A _combined score_ is then computed as a function of the two improvements. There exist several functions which can be used to this end, for instance the _product score function_, which is the default one in the solver which has been used in this project, SCIP #footnote[https://pyscipopt.readthedocs.io/en/latest/index.html].

Formally, let $z$ be the optimal objective function value of the LP at a given node. Let $z_j^0$ and $z_j^1$ be the optimal objective function values of the LPs corresponding to the child nodes where the variable $x_j$ is set to 0 and 1 respectively. $Delta_j^+$ represent the improvement obtained in setting $x_j = 1$, that is $Delta_j^+ = z_j^1 - z$; equivalently, $Delta_j^- = z_j^0 - z$.
The @SB score for variable $x_j$ is then defined as:
$ "score"_P (j) = max(Delta_j^+, epsilon) dot max(Delta_j^-, epsilon) $
with $epsilon = 10^(-6)$ @achterberg2007thesis.

Predicting $"score"_P (j)$ is the goal of the machine learning model which has been trained for this project.

== Machine learning preliminaries
This section recaps the machine learning concepts which are relevant to the experiments presented in this report. The focus is on supervised learning regression, as the goal is to predict the @SB score (which is a continuous value) based on a set of features extracted from the @BnB tree.

=== Linear regression

=== Lasso

=== Decision trees
/*
Decision trees are a powerful and versatile learning technique that uses hyperplanes to partition the input space into several regions, where the behavior of the studied system is simple enough. Each region is defined by a collection of inequalities involving a splitting variable and a split point. While finding the globally optimal tree structure is computationally hard, the tree learning algorithm proceeds greedily to find a local optimum by iteratively splitting nodes to minimize total local loss.

Random forests combine bagging with regression trees. A random forest model consists of multiple regression trees, each trained on a different bootstrap sample. The final prediction is obtained by averaging the individual tree predictions. A key innovation of random forests is a randomization trick that decorrelates the bootstrap models by considering only a random subset of features as splitting candidates at each node, thus reducing the correlation between individual models.

Extremely randomized trees, or ExtraTrees, extend the principles of random forests by introducing even more randomization. As their name suggests, ExtraTrees take the founding ideas behind random forests further, primarily in how they construct the individual trees within the ensemble. This method computes feature importances during the learning procedure, which helps in understanding input-output correlations in the dataset.
*/

=== Bagging and boosting
// Bagging and boosting are two popular ensemble learning techniques that combine multiple models to improve predictive performance. Bagging, or bootstrap aggregating, involves training multiple models independently on different subsets of the training data and averaging their predictions. This reduces variance and helps prevent overfitting. Random forests are a specific implementation of bagging using decision trees, where each tree is trained on a random subset of features.

// Conversely, boosting is a sequential ensemble method that combines weak learners to create a strong learner. In boosting, models are trained iteratively, with each new model focusing on correcting the errors made by the previous ones. This approach reduces bias and can lead to better performance than bagging. Gradient boosting is a popular boosting technique that optimizes a loss function by fitting new models to the residuals of the previous ones.

==== @ERT:both and Random Forests

==== Gradient boosting