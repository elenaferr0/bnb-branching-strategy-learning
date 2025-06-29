# Branch & Bound Strong Branching Approximation with Machine Learning

A research project comparing supervised learning approaches for approximating Strong Branching in Branch & Bound algorithms for Mixed Integer Linear Programming (MILP) problems.

## Overview

This project reproduces and extends the work by Alvarez et al. on using machine learning to approximate Strong Branching (SB) scores in Branch & Bound algorithms. Strong Branching is the most effective strategy for reducing tree size in B&B but is computationally expensive. This research explores supervised learning models that can maintain SB's effectiveness while significantly reducing computational overhead.

## Problem Statement

The goal is to find a regressor that optimally trades off:
- **Correctness** of Strong Branching score predictions
- **Speed** of computation

A slow but accurate model offers little advantage over computing actual SB scores, while a fast but imprecise model would result in large B&B trees and poor solver performance.

## Methodology

The approach consists of three main phases:

1. **Data Collection**: Solve MILP problems using Strong Branching and extract features at each B&B tree node along with branching decision metrics
2. **Model Training**: Train regressors to mimic SB decisions using the extracted dataset
3. **Benchmarking**: Evaluate trained models against SB and other branching strategies on benchmark problems

## Dataset

The project uses diverse MILP problem categories:

| Category | Problems | Variables (avg) | Constraints (avg) | Nodes (avg) | Time (avg) |
|----------|----------|-----------------|-------------------|-------------|------------|
| Random Bin Packing | 91 | 57 | 15 | 230 | 5.93s |
| Random Set Cover | 103 | 88 | 88 | 32 | 7.97s |
| BPEQ | 7 | 195 | 108 | 20,978 | 2,830s |
| MKNSC | 5 | 196 | 130 | 37,378 | 3,875s |
| BPSC | 1 | 112 | 97 | 42,813 | 7,874s |
| MIPLIB | 1 | 201 | 133 | 50 | 35s |

## Features

The model uses 38 features categorized into:
- **Static features**: Problem structure characteristics (cost coefficients, constraint matrix properties)
- **Dynamic features**: Node-specific information that changes during the B&B process
- **Dynamic optimization features**: Features derived from the current LP relaxation solution

## Requirements

Install the required dependencies:

```bash
pip install pyscipopt seaborn imodels lightgbm pymoo
```

## Usage

The main analysis is contained in the Jupyter notebook `bnb_branching_strategy_learning.ipynb`. The notebook includes:

- Data preprocessing and feature engineering
- Model training and hyperparameter tuning
- Performance evaluation and comparison
- Visualization of results

## Documentation

- `report/`: Source code for the experiment report
- `references/paper.pdf`: The paper describing the original experiment

## Key Results

The project evaluates various machine learning models including traditional regressors and tree-based methods, analyzing their trade-offs between prediction accuracy and computational efficiency in the context of MILP solving.

## Trained Models

The project evaluates multiple machine learning approaches for approximating Strong Branching scores:

### Tree-Based Models
- **Extra Trees Regressor**: Ensemble method with randomized splitting for reduced variance
- **Random Forest Regressor**: Bootstrap aggregated decision trees for robust predictions  
- **Decision Tree Regressor**: Single tree with MSE-based splitting criteria
- **Greedy Tree Regressor**: Custom interpretable tree with complexity tracking
- **LightGBM Regressor**: Gradient boosting with leaf-wise tree growth
- **Boosted Rules Regressor**: Interpretable ensemble optimizing logical rules

### Linear Models
- **LASSO Regression**: L1-regularized linear regression with automatic feature selection
- **Linear Regression**: Standard least squares regression baseline

## Model Selection Strategy

Models were selected using a **Pareto-optimal approach** that balances:
- **Prediction accuracy** (measured by MSE and R² score)
- **Computational efficiency** (prediction time during B&B)

The Pareto frontier identifies configurations where no other solution can improve one objective without worsening another. This eliminates dominated solutions that are strictly worse in both accuracy and speed, focusing evaluation on truly competitive trade-offs.

A custom refit strategy identified models on the Pareto frontier and selected the one closest to the centroid of optimal trade-offs, ensuring practical applicability in real-time B&B scenarios.

## Experimental Results

### Model Performance Comparison
Tree-based models significantly outperformed linear approaches:
- **Best performing models**: Extra Trees, Random Forest, and LightGBM regressors
- **R² scores**: Tree models achieved ~0.8-0.9 vs ~0.3-0.4 for linear models  
- **RMSE**: Tree models ~0.3 vs ~1.0 for linear models
- **Prediction speed**: All models maintained sub-second prediction times suitable for B&B

### Benchmarking Against Standard Strategies
Learned branching strategies were evaluated against:
- **Reliability Branching**: Default SCIP strategy combining pseudocosts and strong branching
- **Pseudocost Branching**: Fast but less accurate historical-based decisions
- **Most Infeasible Branching**: Simple variable selection heuristic
- **Random Branching**: Baseline random variable selection

### Key Findings
- **Computational Efficiency**: Learned models achieved significant speedups over exact Strong Branching
- **Solution Quality**: Maintained competitive performance with manageable tree size increases
- **Practical Viability**: Confirmed ML-based approximations can effectively balance accuracy and efficiency
- **Trade-off Optimization**: Successfully identified models in the "knee" region of the Pareto frontier

The results demonstrate that machine learning can successfully approximate Strong Branching while maintaining the critical balance between prediction accuracy and computational speed required for practical MILP solving.