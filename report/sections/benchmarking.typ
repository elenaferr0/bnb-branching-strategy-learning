#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary

#show : init-glossary.with(defs)

= Benchmarking
In the benchmarking phase, the performance of the trained models was compared against other branching strategies. The test set of problems was solved to optimality using the trained models and the results were compared with those obtained using traditional branching strategies. 

Since the trained estimators are likely to perform better than @SB in terms of time, but worse tree size-wise #footnote[SB is the best strategy when it comes to tree size]\, problems have been solved by placing upper bounds on both the time and the tree size. Alvarez et al @alvarez2017bnb used one hour and $10^5$ nodes respectively. Given that `randomSC` and `randomBP` instances are quite smaller, proportioned bounds were used: 0.5, 1 and 5 seconds for time and 100, 200 and 300 for the nodes.

#text("TODO: INSERT TABLES", red, size: 16pt)