import numpy as np

from .random_probs.bin_packing import bin_packing
from .random_probs.set_cover import set_cover
from .random_probs.traveling_salesman import traveling_salesman
from .random_probs.multi_knapsack import multi_knapsack


def generate_datasets(set_cover_instances: int, bin_packing_instances: int, multi_knapsack_instances: int,
                      traveling_salesman_instances: int):
    np.random.seed(0)

    dataset = {}
    sc = set_cover(
        n_problems=set_cover_instances,
        sets=(100, 300),
        elements=(50, 400),
    )
    dataset['SC'] = sc

    bp = bin_packing(
        n_problems=bin_packing_instances,
        items=(100, 300),
        bins=(50, 150),
        bin_capacity=(50, 100),
        item_size=(10, 60),
    )
    dataset['BP'] = bp

    mkp = multi_knapsack(
        n_problems=multi_knapsack_instances,
        items=(100, 300),
        knapsacks=(5, 20),
        knapsack_capacity=(50, 150),
        item_profit=(10, 100),
        item_weight=(5, 50),
    )
    dataset['MKP'] = mkp

    tsp = traveling_salesman(
        n_problems=traveling_salesman_instances,
        cities=(10, 17),
    )
    dataset['TSP'] = tsp

    return dataset
