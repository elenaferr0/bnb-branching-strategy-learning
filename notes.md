# Theory
## Intuitive Branch and Bound
- since we have a convex area the optimal solution will lie in one of the corners
- if integer constraints are added, ILP then the simplex method is not useful (?). No longer any point in the are is a feasible solution but only points inside. So the solution obtained by relaxing integer constraint is not feasible anymore.
- BnB can be used to found the best integer solution
  - relax assumption that variables are integer
  - branch on one of the variables with decimal value (for instance, pick the one with largest fractional part). There are different techniques to branch (e.g. pick one the variables at random)
  - if the branching variable x = 2.56 (if x cannot be between 2 and 3 then it must be either x <= 2 or x >= 3)
  - the new problem is the initial + the new constraint (e.g. x <= 2)
  - the new constraints will remove a part of the feasible region (we can recompute the objective function).
    - for maximization problems: feasible solutions will be LB
    - for minimization problems: feasible solutions will be UB
  - don't stop until the variables are all integer
  - the constraints that should be added to the problem are the path taken to reach the current node
  - if there is no intersection between the feasible region and the new constraints -> no feasible solution
  - fathomed: a solution that was found but is not better than the current best solution. If I had found a better one this would become the new LB (?)

- useful: https://www.ibm.com/docs/en/cofz/12.9.0?topic=optimizer-selecting-variables 
- MKP instances: https://www.researchgate.net/publication/271198281_Benchmark_instances_for_the_Multidimensional_Knapsack_Problem
- B&B strong branching scores: https://community.ibm.com/community/user/discussion/strong-branching-score-at-each-branch-and-bound-node?hlmlt=VT 
- callback:https://github.com/IBMDecisionOptimization/docplex-examples/blob/master/examples/mp/callbacks/branch_callback.py
# References
- MIPLIB: 
  - Achterberg, T., Koch, T., Martin, A.: Miplib 2003. Operations Research Letters 34(4), 361–372 (2006) 
  - Bixby, R., Ceria, S., McZeal, C., Savelsbergh, M.: An updated mixed integer programming library: Miplib 3.0 (1996)
