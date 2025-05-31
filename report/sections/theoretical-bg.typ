#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary

#show : init-glossary.with(defs)
= Theoretical background <sec:theoretical-bg>
== Optimization theory
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

// === Optimality gap
// The optimality gap is a metric which quantifies how close the current best integer solution (known as _incumbent_) is to the actual optimal solution. An incumbent solution is found when either an integer solution is returned by the @LP relaxation, or a leaf of the @BnB tree is reached.

// Given the large size the tree could attain, it is sometimes convenient to stop its exploration once the gap is below a certain threshold @ibm-gap. Let $"UB"$ be the incumbent and $"LB"$ the current best lower bound obtained from @LP relaxations. The relative gap is defined as: $ "gap" = quad & (|"UB" - "LB"|)/(|"UB"|) $
// #linebreak()

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

== Machine learning <sec:ml-theoretical-bg>
This section recaps the machine learning concepts which are relevant to the experiments presented in this report. The focus is on supervised learning, specifically on a regression task which goal is to predict a continuous value corresponding to the @SB score, based on a set of features extracted from the @BnB tree.

More precisely, the goal is not to find the best overall model, but rather the one which is able to better trade-off the correctness of the prediction with the time it takes to compute it. This is because in a later phase the model will be integrated in a @BnB solver, where it will be used to guide the branching process on the resolution of a set of benchmark problems.
 In this context, a slow but highly accurate model would not be much more useful than actually computing @SB scores, while a fast but imprecise one would yield fairly large @BnB trees and thus influence negatively the solver's performance. Since these trees can have infinitely many nodes and in each of them the model will be asked to predict scores for every fractional variable, even a small increase in the prediction time can have a significant impact on the solution time.

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