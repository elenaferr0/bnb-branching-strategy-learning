import numpy as np

from dataset.generated.traveling_salesman import traveling_salesman
from generated.multi_knapsack import multi_knapsack

if __name__ == "__main__":
    np.random.seed(0)

    # sc = set_cover(
    #     n_problems=1,
    #     sets=(100, 300),
    #     elements=(50, 400),
    # )

    # bp = bin_packing(
    #     n_problems=1,
    #     items=(100, 300),
    #     bins=(50, 150),
    #     bin_capacity=(50, 100),
    #     item_size=(10, 60),
    # )

    # mkp = multi_knapsack(
    #     n_problems=1,
    #     items=(100, 300),
    #     knapsacks=(5, 20),
    #     knapsack_capacity=(50, 150),
    #     item_profit=(10, 100),
    #     item_weight=(5, 50),
    # )

    tsp = traveling_salesman(
        n_problems=1,
        cities=(10, 17),
    )

    for s in tsp:
        name, types, c, A, b, bnd = s
        print(f"Name: {name}, Types: {types}, c: {c}, A: {A}, b: {b}, bnd: {bnd}")
