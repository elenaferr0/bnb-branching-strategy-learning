#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary

#show : init-glossary.with(defs)
= Dataset generation <sec:dataset-gen>
== Problems
== Features
The intuition Alvarez et al. proposed in their work is that at each node of the @BnB tree, other than determining the scores for each fractional variable the solver also computes a set of features which are then used to train the models @orig-paper. 
According to the authors, the feature computation must be efficient enough to not affect the overall performance of the solver, while also being independent of the problem size #footnote[If it wasn't, the learned models would only be able to approximate scores for problems of a fixed size.] 
and of irrelevant changes such as rows or columns reordering.
// TODO
#figure(table(columns: (1fr, 1fr, 1fr), [], [], []), caption: "Computed features")

== Solver
For the purposes of this project, the Python APIs for IBM CPLEX 22.11 were used, specifically through packages `docplex` and `cplex` #footnote[The said libraries #link("https://ibmdecisionoptimization.github.io/docplex-doc/getting_started_python.html", "officially support up to Python version 3.7.x"), however they still work up to version 3.9.6, which has been used for this project. ]. The former
offers a high-level interface for modeling and solving optimization problems, while the latter provides direct access to the CPLEX solver.
Employing C or C++ APIs would have been considerably more efficient, given the burden of solving problems with the @SB strategy. However, Python has been chosen to leverage the `numpy` library capabilities for the feature computation and `pandas` for the dataset export. Furthermore, integrating the trained models predictions with the solver is trivial with Python.

The solver was configured so that heuristics, cuts and presolve options were disabled; this ensures the @BnB algorithm only is employed for the problem resolution.

=== Branching scores and features extraction
To extract the branching scores and compute the features from the problem at each @BnB tree node, a custom branching callback has been implemented. This CPLEX functionality comes in handy to define custom branching strategies, as it enables the user to decide which variable to branch on and whether to perform prunings. 

A `CustomBranching` class containing common logic for callbacks was implemented, so that new callbacks can be added with ease by simply defining the variable selection method.
For the purposes of this project, two callbacks have been realized:
- `StrongBranching`, used at dataset generation time to extract @SB scores and features;
- `LearnedBranching`, used to assess the performance of the learned models.