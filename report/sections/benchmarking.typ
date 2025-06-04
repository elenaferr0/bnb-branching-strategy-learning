#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary
#import "../utils.typ": *

#show : init-glossary.with(defs)

= Benchmarking
In the benchmarking phase, the performance of the trained models was compared against other branching strategies. The test set of problems was solved to optimality using the trained models and the results were compared with those obtained using traditional branching strategies. 

Since the trained estimators are likely to perform better than @SB in terms of time, but worse tree size-wise #footnote[This is true because SB is the best known strategy when it comes to tree size.]\, problems have been solved by placing upper bounds on both the time and the tree size. Alvarez et al @alvarez2017bnb used one hour and $10^5$ nodes respectively. Given that `randomSC` and `randomBP` instances are quite smaller, proportioned bounds were used: 0.5, 1 and 5 seconds for time and 100, 200 and 300 for the nodes.

#let bench-table = (data, caption, label) => [#figure(table(
      columns: 3,
      table.header("Strategy", "Time Reduction (%)", "Nodes Increase (%)"),
      ..data.pairs().map(((name, (time-reduction, nodes-increase))) => (
        raw(name),
        [#format(time-reduction, 2)%],
        [#format(nodes-increase, 2)%],
      )).flatten()
    ),
  caption: caption,
  ) #label
]

#let small-probs = (
  "learnedstrongbrnch": (time-reduction: 57.54, nodes-increase: 102.62),
  "mostinf": (time-reduction: 56.55, nodes-increase: 108.67),
  "pscost": (time-reduction: 56.81, nodes-increase: 75.22),
  "random": (time-reduction: 53.36, nodes-increase: 100.54),
  "relpscost": (time-reduction: 67.11, nodes-increase: 72.46)
)

#let large-probs = (
  "learnedstrongbrnch": (time-reduction: 10.15, nodes-increase: 172.40),
  "mostinf": (time-reduction: 28.80, nodes-increase: 197.97),
  "pscost": (time-reduction: 61.97, nodes-increase: 237.14),
  "random": (time-reduction: 29.66, nodes-increase: 145.72),
  "relpscost": (time-reduction: 10.56, nodes-increase: 183.26)
)

#ref(<tab:small-probs>) and #ref(<tab:large-probs>) show the results of the comparison between the trained models, standard branching strategies and the original @SB approach.

#grid(
  columns: 2,
  column-gutter: 10pt,
  bench-table(
    small-probs,
   "Benchmarking results for small problems (randomSC and randomBP instances)",
   <tab:small-probs>
  ),
  bench-table(
    large-probs,
    "Benchmarking results for large problems (bpeq, bpsc, miplib, mknsc instances)",
    <tab:large-probs>
  ),
)

All strategies proved are considerably faster than the original @SB approach, with solution times being from 10% to 67% shorter. While this represents an improvement, it falls short of the 85% decrease in solving time obtained by Alvarez et al.. Hence, the trained predictors actually performed worse than the benchmarks established in that prior experiment.

Furthermore, the number of nodes increased notably, by around 80% for small problems and over 170% for bigger ones. This percentage is rather high, yet it aligns roughly with increases observed in other branching strategies. This suggests that the learned branching strategy is not excellent at reducing tree size, but it is at least slightly better than random and most infeasible branching; given the nature of these, this is rather reasonable.

#let predictors-benchmark = (
  "BoostedRulesRegressor": (nodes-increase: 95.86, time-decrease: 51.92, gap: 0.42),
  "DecisionTreeRegressor": (nodes-increase: 95.45, time-decrease: 55.62, gap: 0.39),
  "ExtraTreeRegressor": (nodes-increase: 97.99, time-decrease: 44.56, gap: 0.41),
  "GreedyTreeRegressor": (nodes-increase: 113.63, time-decrease: 47.77, gap: 0.37),
  "LGBMRegressor": (nodes-increase: 108.66, time-decrease: 47.19, gap: 0.39),
  "Lasso": (nodes-increase: 159.44, time-decrease: 55.23, gap: 0.42),
  "LinearRegression": (nodes-increase: 127.58, time-decrease: 55.53, gap: 0.44),
  "RandomForestRegressor": (nodes-increase: 106.32, time-decrease: 44.12, gap: 0.38)
) 


#ref(<tab:predictors-benchmark>) summarizes results obtained by using each estimator to predict branching scores. Tree-based models are in general performing better than linear ones size-wise, however with regards to time, linear model predictions tend to be faster, thus producing a larger decrease. This is consistent with the results of the learning phase.


#figure(
  table(
    columns: 4,
    table.header("Predictor", "Nodes Increase", "Time Decrease", "Gap"),
    ..predictors-benchmark.pairs().map(((name, (nodes-increase, time-decrease, gap))) => (
      raw(name),
      [#format(nodes-increase, 2)%],
      [#format(time-decrease, 2)%],
      [#format(gap, 2)]
    )).flatten()
  ),
  caption: "Benchmarking results aggregated by predictor",
) <tab:predictors-benchmark>