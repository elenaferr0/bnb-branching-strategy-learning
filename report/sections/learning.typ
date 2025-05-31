#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary

#show : init-glossary.with(defs)
= Experiments <sec:experiments>
This section illustrates the different machine learning techniques which were leveraged to approximate the strong branching procedure in the @BnB algorithm.
== Learning
=== Feature engineering
// SimpleImputer(strategy='constant', fill_value=0): This step in the pipeline handles missing values by replacing them with a constant value, specifically 0, in the input features.
// StandardScaler(): This step scales the features so they have a mean of 0 and a standard deviation of 1, which is important for many machine learning algorithms that are sensitive to feature scales.
// regressor: This is the actual machine learning model (like a linear regression or a random forest) that will be trained on the preprocessed features to make predictions.
// np.log1p: This function transforms the target variable (what you're trying to predict) by applying the natural logarithm of (1 + x). This is often used to handle target variables that are skewed or have a wide range, making them more suitable for regression models.
// np.expm1: This function is the inverse transformation of np.log1p; it converts the predicted logarithmic values back to their original scale, ensuring the final predictions are in a meaningful unit.
// Pipeline: This Scikit-learn tool sequences multiple data processing steps (like imputation and scaling) and a final estimator (the regressor) into a single, cohesive object, ensuring transformations are applied consistently.
// TransformedTargetRegressor: This meta-estimator wraps a regressor and applies a transformation to the target variable before training and then automatically inverse-transforms the predictions, simplifying the handling of transformed targets.


=== Pipeline 
A pipeline sequentially chains together multiple data processing steps and a final estimator into a single object. One has been created for each of the trained regressor; this ensures that identical transformations are applied to features during the benchmarking phase.

The pipeline is composed of the following steps:
- Simple Imputer: fills in any missing values by replacing them with zero;
- Standard Scaler: adjusts features so they all have the same scale, making them easier for the model to work with;
- Transformed Target Regressor: it's meta-estimator which wraps a regressor and applies a transformation to the target variable before training and then automatically inverse-transforms the predictions. Applying a logarithmic function to train data renders learning easier, as it enables to
  spread out values clustered near zero and _compress_ larger values. Differently to what the original experiment suggested, experiments with logarithm plus one turned out to perform better than the simple logarithm.#footnote[ What matters is the ranking of scores for different variables, rather than the actual value. Since logarithm is a uniformly increasing function, applying the it to the target will not affect the quality of predictions. ]

=== Metrics
The following metrics have been employed to evaluate the performance of the trained regressors:
- the coefficient of determination $r^2$, which is a measure representing the proportion of variance for dependent variable that's explained by an independent variable in a regression model. It represents how well the predictions approximate real data points, with 1 being the highest and 0 the lowest @cohen1988statanalysis;
- the @MSE, which measures the average difference between the estimated and the actual value. It corresponds to the expected value of the squared error loss, and serves to quantify the _average magnitude of the errors_. This metric is not expressed in same unit of measure as original data; to obtain such kind of measure, it's sufficient to take the square root, and the returned value corresponds to the @RMSE @hodson2022rmse.

#text("TODO: MISSING METRICS?", red, size: 16pt)

=== Hyperparameter tuning
Grid Search CV has been used to perform hyperparameter tuning; it works by systematically exploring a defined range of hyperparameter values to identify the combination that yields the best model performance. This exhaustive search ensures that the optimal hyperparameters. 

Cross validation is an integral part of Grid Search; it's an approach which consists in splitting the dataset in multiple folds, then the model is trained and validated on different combinations of these folds to provide a more robust estimate of its performance

==== Refit strategy
As mentioned in #ref(<sec:ml-theoretical-bg>), the goal is to find the best trade-off between a prediction error and scoring time; for this reason, a custom refit strategy has been defined. This function takes the result of cross validation and returns the best estimator which will be then refit automatically by `GridSearchCV`.

Finding the best estimator means minimizing at the same time both the @MSE:long and the scoring time evaluated during cross validation; this can be accomplished by solving a multi-objective optimization problem, whose solutions collectively form the Pareto optimal set @roy2023optimization.
Intuitively, for Pareto optimal estimators there is no way to improve @MSE without simultaneously worsening the scoring time and vice versa. In the general case, more than one estimator will have this property; the one nearest to the centroid of the Pareto set points is then chosen, as it represents the _best compromise solution_.

#text("TODO: CHART", red, size: 16pt)

=== Results
// Brief tables of results (like the one printed by metrics)
// chart for results
