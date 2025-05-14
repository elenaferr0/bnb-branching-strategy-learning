#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary
#import "../variables.typ": *

#show : init-glossary.with(defs)

= Introduction
== Problem statement and motivation
== Theoretical background
This section aims to provide the reader with a brief overview of theoretical concepts needed to understand results presented in this report, both from an optimization theory and a machine learning perspective.

=== Optimization problems
Throughout this report, @ILP optimization problems of the following (standard) form are considered:
$
 min quad & c^T x\
 s.t. quad & A x <= b \
 &x_i in {0, 1} space forall i in I
$

where $c in #R^n$ (the cost vector), $A in #R^(m times n)$ (the coefficient matrix), $b in #R^m$ (the right-hand side vector) and $x in {0, 1}^n$ (decision variables vector). $I$ is the set of indices of binary decision variables.
Theoretically speaking, any of the considerations made in this experiment can be extended to the general @MILP case, by introducing suitable constraints for continuous variables #footnote[$x_j in #R _+ forall j in C$, with $C$ being the set of continuous variables indices]. However, to shorten dataset generation times only binary problems have been considered.

=== Branch and Bound
@BnB is one of the most widely used algorithms to solve @MILP problems.

==== @SB:both

=== Decision trees

=== @ERT:both

=== @PCA:both

=== Rule-based classifiers
