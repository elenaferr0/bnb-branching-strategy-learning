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

Below is a brief recap of the characteristics of techniques which have been evaluated in this project.

- Linear Regression: a statistical method that models the relationship between a dependent variable and one or more independent variables by fitting a linear equation to the observed data. It assumes a linear relationship and aims to minimize the @MSE;

- @LASSO: an extension of linear regression that adds a penalty term proportional to the absolute value of the magnitude of the coefficients. This penalty forces some coefficients to be exactly zero, effectively performing feature selection and improving model interpretability;

- Decision Trees: they can be used for both classification and regression; the idea is to learn simple decision rules inferred from the data features, creating a tree-like model of decisions and their possible consequences. Decision trees can handle both numerical and categorical data and are easy to interpret;

- Bagging and Boosting: these are ensemble methods that combine multiple models to improve overall predictive performance. Bagging (e.g., Random Forests) builds independent models from bootstrapped samples and averages their predictions, reducing variance. Boosting (e.g., Gradient Boosting) builds models sequentially, with each new model trying to correct the errors of the previous ones, primarily reducing bias.

- @ERT and Random Forests: both are ensemble methods using Decision Trees. Random Forests build multiple decision trees on bootstrapped samples of the data and randomly select a subset of features at each split point. @ERT go a step further by randomly choosing both the feature and the split point, further increasing randomness and often reducing variance.

- Gradient Boosting: a powerful boosting technique where new models are fit to the residuals (errors) of the previous models in a sequential manner. It uses a gradient descent optimization algorithm to minimize the loss function, iteratively improving the model's predictions.