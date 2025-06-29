#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary
#import "../utils.typ": *

#show : init-glossary.with(defs)

= Benchmarking
In the benchmarking phase, the performance of the trained models was compared against other branching strategies. The set of benchmark problems was solved to optimality using the trained models and the results were compared with those obtained using traditional branching strategies. 

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

/*
strategy 	n_nodes_bench 	time_bench 	gap_bench 	n_nodes_stats 	time_stats 	n_vars_stats 	n_constraints_stats 	time_reduction 	nodes_increase 	solved_instances
0 	learnedstrongbrnch 	153.919543 	7.717844 	0.404042 	110.856863 	18.536129 	72.156835 	52.647482 	57.537283 	102.621500 	695
1 	mostinf 	159.450758 	7.727990 	0.397456 	112.497273 	18.089986 	69.068182 	46.670455 	56.552938 	108.674065 	88
2 	pscost 	160.096296 	7.823590 	0.415214 	115.898667 	17.892652 	67.988889 	44.633333 	56.814968 	75.215533 	90
3 	random 	169.280488 	8.119749 	0.398825 	110.285854 	17.414776 	67.463415 	42.524390 	53.361248 	100.536326 	82
4 	relpscost 	162.748858 	5.933811 	0.321713 	123.274521 	18.523974 	70.931507 	48.630137 	67.111007 	72.457689 	73

Large Benchmarks (mknsc, bpeq, bpsc, miplib) - Performance by Strategy:

	strategy 	n_nodes_bench 	time_bench 	gap_bench 	n_nodes_stats 	time_stats 	n_vars_stats 	n_constraints_stats 	time_reduction 	nodes_increase 	solved_instances
0 	learnedstrongbrnch 	57845.792408 	1889.706370 	0.389898 	30848.979592 	4173.120638 	187.714286 	122.387755 	0.064101 	178.483645 	98
1 	mostinf 	62373.833333 	1660.214792 	0.385546 	29663.500000 	3723.852001 	183.750000 	119.416667 	25.853209 	209.918158 	12
2 	pscost 	59125.454545 	875.680417 	0.220965 	30329.909091 	4266.195594 	192.181818 	123.818182 	64.178824 	228.599174 	11
3 	random 	58258.000000 	3462.309460 	0.448142 	33796.769231 	4675.035687 	186.000000 	122.076923 	36.086132 	140.806398 	13
4 	relpscost 	51759.666667 	1392.170307 	0.285890 	26169.833333 	3028.746607 	191.416667 	123.916667 	-3.007411 	177.109822 	12

*/

#let small-probs = (
  "learnedstrongbrnch": (time-reduction: 57.54, nodes-increase: 102.62),
  "mostinf": (time-reduction: 56.55, nodes-increase: 108.67),
  "pscost": (time-reduction: 56.81, nodes-increase: 75.22),
  "random": (time-reduction: 53.36, nodes-increase: 100.54),
  "relpscost": (time-reduction: 67.11, nodes-increase: 72.46)
)

#let large-probs = (
  "learnedstrongbrnch": (time-reduction: 6.41, nodes-increase: 178.48),
  "mostinf": (time-reduction: 25.85, nodes-increase: 209.92),
  "pscost": (time-reduction: 64.18, nodes-increase: 228.60),
  "random": (time-reduction: 36.09, nodes-increase: 140.81),
  "relpscost": (time-reduction: -3.01, nodes-increase: 177.11)
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

All strategies proved are considerably faster than the original @SB approach, with solution times being from 10% to 67% shorter. While this represents an improvement, it falls short of the 85% decrease in solving time obtained by Alvarez et al.. Hence, the trained predictors actually performed worse than the benchmarks established in that prior experiment @alvarez2017bnb.
Furthermore, the number of nodes increased notably, by around 80% for small problems and over 170% for bigger ones. This percentage is rather high, yet it aligns roughly with increases observed in other branching strategies. This suggests that the learned branching strategy is not excellent at reducing tree size, but it is at least slightly better than random and most infeasible branching and, given the nature of these, this is rather reasonable.

#let predictors-benchmark = (
  "BoostedRulesRegressor": (nodes-increase: 96.08, time-decrease: 52.38, gap: 0.42),
  "DecisionTreeRegressor": (nodes-increase: 93.99, time-decrease: 54.57, gap: 0.39),
  "ExtraTreeRegressor": (nodes-increase: 95.47, time-decrease: 44.10, gap: 0.42),
  "GreedyTreeRegressor": (nodes-increase: 112.97, time-decrease: 48.42, gap: 0.36),
  "LGBMRegressor": (nodes-increase: 105.81, time-decrease: 47.85, gap: 0.39),
  "Lasso": (nodes-increase: 159.99, time-decrease: 56.31, gap: 0.42),
  "LinearRegression": (nodes-increase: 126.25, time-decrease: 55.17, gap: 0.43),
  "RandomForestRegressor": (nodes-increase: 104.27, time-decrease: 44.14, gap: 0.38)
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