#import "@preview/glossy:0.8.0": *

#let defs = (
    LP: (
      short: "LP",
      long: "Linear Programming",
    ),
    ILP: (
      short: "ILP",
      long: "Integer Linear Programming",
      plural: "ILP",
      longplural: "Integer Linear Programming problems"
    ),
    MILP: (
      short: "MILP",
      long: "Mixed Integer Linear Programming",
      plural: "MILP",
      longplural: "Mixed Integer Linear Programming problems"
    ),
    BnB: (
      short: "B&B",
      long: "Branch and Bound"
    ),
    SB: (
      short: "SB",
      long: "Strong Branching"
    ),
    PCB: (
      short: "Pseudo Cost Branching",
    ),
    ERT: (
      short: "ERT",
      long: "Extremely Randomized Trees",
      plural: "ERTs",
      longplural: "Extremely Randomized Trees"
    ),
    PCA: (
      short: "PCA",
      long: "Principal Component Analysis",
    ),
    SC: (
      short: "SC",
      long: "Set Cover",
    ),
    BP: (
      short: "BP",
      long: "Bin Packing",
    ),
    MKP: (
      short: "MKP",
      long: "Multiple Knapsack Problem",
    ),
    MSE: (
      short: "MSE",
      long: "Mean Squared Error",
    ),
    RMSE: (
      short: "RMSE",
      long: "Root Mean Squared Error",
    ),
)

#show: init-glossary.with(defs)
