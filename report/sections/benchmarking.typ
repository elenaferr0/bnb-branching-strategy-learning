#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary

#show : init-glossary.with(defs)

= Benchmarking
In the benchmarking phase, the performance of the trained models was compared against other branching strategies. The test set of problems was solved to optimality using the trained models and the results were compared with those obtained using traditional branching strategies. 

Since the trained estimators are likely to perform better than @SB in terms of time, but worse tree size-wise #footnote[This is true because SB is the best known strategy when it comes to tree size.]\, problems have been solved by placing upper bounds on both the time and the tree size. Alvarez et al @alvarez2017bnb used one hour and $10^5$ nodes respectively. Given that `randomSC` and `randomBP` instances are quite smaller, proportioned bounds were used: 0.5, 1 and 5 seconds for time and 100, 200 and 300 for the nodes. These have been chosen by looking at the performance of the @SB strategy on the training set. 

#text("TODO: INSERT TABLE", red, size: 16pt)

All strategies proved are considerably faster than the original @SB approach, with solution times being from 29% to 79% shorter. While this represents an improvement, it falls short of the 85% decrease in solving time obtained by Alvarez et al.. Hence, the trained predictors actually performed worse than the benchmarks established in that prior experiment.

Furthermore, the number of nodes increased notably, by around 80% for small problems and over 170% for bigger ones. This percentage is rather high, yet it aligns roughly with increases observed in other branching strategies. This suggests that the learned branching strategy is not excellent at reducing tree size, but it is at least slightly better than random and most infeasible branching; given the nature of these, this is rather reasonable.