#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary
#import "../utils.typ": *

#show : init-glossary.with(defs)
= Experiments <sec:experiments>
This section illustrates the different machine learning techniques which were leveraged to approximate the strong branching procedure in the @BnB algorithm.
== Learning
=== Pipeline 
A pipeline sequentially chains together multiple data processing steps and a final estimator into a single object. One has been created for each of the trained regressor; this ensures that identical transformations are applied to features during the benchmarking phase.

Each pipeline is composed of the following steps:
- Simple Imputer: fills in any missing values by replacing them with zero;
- Standard Scaler: adjusts features so they all have the same scale, making them easier for the model to work with;
- Select K Best: selects the $k = 20$ best features based on a scoring function, in this case `f_regression`; it evaluates the relationship between each feature and the target variable, selecting those that have the strongest linear correlation;
- Transformed Target Regressor: it's a meta-estimator which wraps a regressor and applies a transformation to the target variable before training and then automatically inverse-transforms the predictions. Applying a logarithmic function to train data renders learning easier, as it enables to
  spread out values clustered near zero and _compress_ larger values. Differently to what the original experiment suggested, experiments with logarithm plus one function turned out to perform better than the simple logarithm#footnote[Logarithmically-scaled predictions could theoretically be used as well, given that what matters is the ranking of scores for different variables, rather than their actual value. Logarithm is a uniformly increasing function, hence applying the it to the target would not affect the quality of predictions.] @alvarez2016thesis.

=== Metrics
To evaluate the performance of the trained regressors, the following metrics have been employed:
- the coefficient of determination $R^2$, which is a measure representing the proportion of variance for dependent variable that's explained by an independent variable in a regression model. It represents how well the predictions approximate real data points, with 1 being the highest and 0 the lowest @cohen1988statanalysis;
- the @MSE, which measures the average difference between the estimated and the actual value. It corresponds to the expected value of the squared error loss, and serves to quantify the _average magnitude of the errors_. This metric is not expressed in same unit of measure as original data; to obtain such kind of measure, it's sufficient to take the square root, and the returned value corresponds to the @RMSE @hodson2022rmse.

=== Hyperparameter tuning
Grid Search CV has been used to perform hyperparameter tuning; it works by systematically exploring a defined range of hyperparameter values to identify the combination that yields the best model performance. This exhaustive search ensures that the optimal hyperparameter configuration is selected.

K-fold cross validation is an integral part of Grid Search; it's an approach which consists in splitting the dataset in $k$ folds, then the model is trained and validated on different combinations of these to provide a more robust estimate of its performance. In this case, the dataset has been split into 5 folds.

==== Refit strategy
As mentioned in #ref(<sec:ml-theoretical-bg>), the goal is to find the best trade-off between a prediction error and scoring time; for this reason, a custom refit strategy has been defined. This function takes the result of cross validation and returns the best estimator which will be then refit automatically by `GridSearchCV`.
Finding the best estimator means minimizing at the same time both the @MSE and the scoring time evaluated during cross validation. This can be accomplished by solving a multi-objective optimization problem, whose solutions collectively form the Pareto optimal set @roy2023optimization.
Intuitively, for Pareto optimal estimators there is no way to improve the @MSE without simultaneously worsening the scoring time and vice versa. In the general case, more than one estimator will have this property; the one nearest to the centroid of the Pareto set points is then chosen, as it represents the _best compromise_ solution.

#ref(<img:params-tradeoff>) shows plot where each point is a different hyperparameter configuration evaluated by Grid Search. The x-axis represents the @MSE, while the y-axis represents the scoring time in seconds. Points in green belong to the Pareto optimal set; the chosen one is highlighted in orange.

#figure(image(
  "../imgs/params_tradeoff.png",
  width: 55%
),
caption: "Trade-off between MSE and scoring time for different params (Decision Tree)",) <img:params-tradeoff>


=== Results
#let results = (
  "ExtraTreeRegressor": (r2: 0.829620, mse: 0.215618, rmse: 0.462997, time: 0.038954),
  "RandomForestRegressor": (r2: 0.937185, mse: 0.080208, rmse: 0.280036, time: 0.048526),
  "DecisionTreeRegressor": (r2: 0.928140, mse: 0.090546, rmse: 0.299405, time: 0.022248),
  "Lasso": (r2: 0.153085, mse: 1.067132, rmse: 1.031740, time: 0.028760),
  "LinearRegression": (r2: 0.153211, mse: 1.066975, rmse: 1.031663, time: 0.026648),
  "GreedyTreeRegressor": (r2: 0.726101, mse: 0.346697, rmse: 0.586997, time: 0.021616),
  "BoostedRulesRegressor": (r2: 0.805683, mse: 0.247500, rmse: 0.494309, time: 0.065747),
  "LGBMRegressor": (r2: 0.717957, mse: 0.357070, rmse: 0.595730, time: 0.040210)
)

#ref(<tab:learning-results>) shows the performance of different models with K-fold Cross Validation, evaluated using the metrics described above. The results indicate that Random Forest Regressor achieved the highest $R^2$ score. A RMSE value around one for Lasso and Linear Regression indicates that for most samples the predicted value is between 2 and 4 times the actual score. This result is not entirely satisfactory, although since only the relative order between scores is important to the @BnB algorithm, rather than the actual value, these models might still be useful in practice. For this reason they have been included in the benchmark phase.
Generally, tree-based models outperformed linear ones, with Decision Trees and @ERT also showing strong performance. This is likely ascribed by the likely non-linear relationship between the features and the target variable, which tree-based models are better suited to capture.

#figure(
  table(
    columns: 5,
    table.header("Model", "R² Score", "MSE", "RMSE", "Score Time (s)"),
    ..results.pairs().map(((name, (r2, mse, rmse, time))) => (
      raw(name),
      [#format(r2, 2)],
      [#format(mse, 6)],
      [#format(rmse, 6)],
      [#format(time, 6)]
    )).flatten()
  ),
  caption: "Performance of different models on the benchmark set",
) <tab:learning-results>


#ref(<img:performance-tradeoff>) shows the trade-off between @MSE and scoring time for different estimators. Ideally, optimal models should be as close as possible to the bottom left corner. The chart highlights that Decision Trees offer the best compromise, followed by @ERT, Random Forests and Greedy Tree Regressor.

#figure(image(
  "../imgs/models_tradeoff.png",
  width: 60%
),
caption: "Trade-off between MSE and scoring time for different models",
) <img:performance-tradeoff>