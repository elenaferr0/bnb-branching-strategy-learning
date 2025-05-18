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

- MKP instances: https://www.researchgate.net/publication/271198281_Benchmark_instances_for_the_Multidimensional_Knapsack_Problem
- B&B strong branching scores: https://community.ibm.com/community/user/discussion/strong-branching-score-at-each-branch-and-bound-node?hlmlt=VT 
- useful explanation of regression metrics https://scikit-learn.org/stable/modules/model_evaluation.html#r2-score
- https://github.com/scipopt/PySCIPOpt/issues/447

Default branching rules:
```
 branching rule       priority maxdepth maxbddist  description
 --------------       -------- -------- ---------  -----------
 relpscost               10000       -1    100.0%  reliability branching on pseudo cost values
 pscost                   2000       -1    100.0%  branching on pseudo cost values
 inference                1000       -1    100.0%  inference history branching
 mostinf                   100       -1    100.0%  most infeasible branching
 leastinf                   50       -1    100.0%  least infeasible branching
 distribution                0       -1    100.0%  branching rule based on variable influence on cumulative normal distribution of row activities
 fullstrong                  0       -1    100.0%  full strong branching
 cloud                       0       -1    100.0%  branching rule that considers several alternative LP optima
 lookahead                   0       -1    100.0%  full strong branching over multiple levels
 multaggr                    0       -1    100.0%  fullstrong branching on fractional and multi-aggregated variables
 allfullstrong           -1000       -1    100.0%  all variables full strong branching
 vanillafullstrong       -2000       -1    100.0%  vanilla full strong branching
 random                -100000       -1    100.0%  random variable branching
 nodereopt            -9000000       -1    100.0%  branching rule for node reoptimization
```

# References
- MIPLIB: 
  - Achterberg, T., Koch, T., Martin, A.: Miplib 2003. Operations Research Letters 34(4), 361–372 (2006) 
  - Bixby, R., Ceria, S., McZeal, C., Savelsbergh, M.: An updated mixed integer programming library: Miplib 3.0 (1996)
- branching rules revisited https://pdf.sciencedirectassets.com/271697/1-s2.0-S0167637700X01733/1-s2.0-S0167637704000501/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEHEaCXVzLWVhc3QtMSJHMEUCIHWw7qk%2BhHfQE25r3mE%2FiqBszA%2BDKjbawCrBoYAX2zuEAiEAgxEHnwDfT8cIvrxTJvYiYdoAT1oI4cIAVzoXUHlORoYqswUIGhAFGgwwNTkwMDM1NDY4NjUiDJDvZqfg4FTmgd0eByqQBWAPJ7ICAjQYdxy90AJBmiqgMuK9Cgs4nrwuJCeE0sWZkCeYkUKeB7RNydtt3MfFX9nN6c%2FUyG4o%2BVGnh2BD%2FU9m3ps4avktPXxAOecU%2FVgqtlu75Aiv%2BACtJjm7nzBJ1InX3U6OplJvE90flqXNzDDBj9%2BiSm29am77y3nps19Bfzhli4vl%2FGzMAerFr7jula3Rtw2ihexYVab%2Fe2J16AX2z0JcXj8MtJDZGin3w%2FIHaV5w7V8M7usrK0Z0BS32cfUwFYgqfCkLuhv8MrBWdUPbkUNdEAhRypXIED5KmgYXZQ8s6lX7%2F8%2BR%2BIgEFXHhMmp8sKDf8xXgsEBJxdsy2AMLwol8GuGnRmycIysphtB7qUUWpYhm3eigpc7wRD0kBZv5eWxuKuRxaxoK5aJftaZmt2%2B4eGAJR0mkQ0wY%2BBA%2F8nmWbz9sxHiHizzm%2BjMHHR8RJe8thCiFoW4yaG3aLknsAjbc9QZ2xnvlMgruFzedVqwYloxnrJblzwW6DHsf3kYJFPqGJe04NKvkonTQXZlbB%2BDmWIcMaE3xxV38yJ8JgQD9n6bpetvy89R7kVOPbFIfD4TgkcffF1uTZ8n7%2BlGwvWBRg8tSdhnFZuaH271%2Bw1wl6LHU%2FlPX2ftr2hsTG1X2oFX17r952UoJ%2BgrByvGMd%2FoiLnvGQ9mhLpMMxFYiCBQA5Gl2wzF2eBQ%2FNof5ol%2F4YVpnvB4s8wqv0SuRiQfXEsAIeJlyYFfQgSvKTLn8%2BWcAxgtw9uqvr%2BYBkWn2VCbz1C3xGijl0PJJKVml70cqd4f7GJ36sYqWtHV6%2BJ5xcGxzJGpqCuhpQsoc660FY%2Fr8wldFWHDc%2FJo%2F%2F%2BPVicggVS9X7FNsGR%2BtBFXQm9aVMPOq3sAGOrEBOfrDyNoQeD4xlaYN6WI7DXKBZHB9CytDieV9ShVF61VNtgw%2FGL4UTyyoxmXk2PXqbTTkiHTawhYNtSkISx8PQtHJuOGhM7a6DKg7Ahq3WSwq2OX%2Bf60JqWuEOsB3mD5vshd8RX4c26EEVcPfjydTZc4ttS3P09rxkPq4FQ0%2BES7i0heIjo3VrMBqmQIlRTDJvJiH2w6feuUnijXhgxRBBPI%2BPhBk6c0piVIeBjkM%2FItc&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250504T170359Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYT3FLDW6J%2F20250504%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=cacce27a804fa11ee2ec92eba4bf3ca111ac93c4d1a0bf36f6044ed01b16f3b7&hash=d3c251703383b1a96ed7cad0749d07c8010630084c05ac520af44011b89a017a&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0167637704000501&tid=spdf-97445cd1-095f-4b5a-a2bb-bd31aadab905&sid=08c7f465686d574caf1bb5c493ecb650db58gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&rh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=0f1a5f50015c59565407&rr=93a9931cbcd95249&cc=it 
- Alejandro Marcos Alvarez, Quentin Louveaux, and Louis Wehenkel. A machine learning-based approximation of strong branching. INFORMS Journal on Computing, 29(1):185–195, 2017. 
- P. Geurts, D. Ernst., and L. Wehenkel, “Extremely randomized trees”, Machine Learning, 63(1), 3-42, 2006. 

- strong branching scores definition https://henrilefebvre.com/idol/tutorials/mixed-integer-programming/dantzig-wolfe/strong-branching.html
- strong branching paper: https://www2.isye.gatech.edu/~sdey30/Strongbranching.pdf
- https://www.sciencedirect.com/science/article/abs/pii/S0377221721010018