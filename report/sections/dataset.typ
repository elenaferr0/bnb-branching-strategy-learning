= Dataset generation
== Problems
== Features
== Solver
For the sake of this project, the Python APIs for CPLEX 22.11 were used, specifically through packages `docplex` and `cplex` #footnote[The said libraries #link("https://ibmdecisionoptimization.github.io/docplex-doc/getting_started_python.html", "officially support up to Python version 3.7.x"), however they still work up to version 3.9.6, which has been used for this project. ]. The former
offers a high-level interface for modeling and solving optimization problems, while the latter provides direct access to the CPLEX solver.

Employing C or C++ APIs would have been considerably more efficient, given the burden of solving problems with the strong branching strategy. However, Python has been chosen in order to leverage libraries `numpy` for the feature computation and `pandas` for the dataset export. Furthermore, integrating the trained models predictions with the solver is trivial if using Python.


=== Configuration

=== Branching scores extraction