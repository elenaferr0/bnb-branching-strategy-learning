from dataset.sources.problems.bin_packing import bin_packing
from dataset.sources.problems.set_cover import set_cover
from dataset.sources.problems.traveling_salesman import traveling_salesman
from dataset.sources.problems.multi_knapsack import multi_knapsack


def generate_datasets(set_cover_instances: int, bin_packing_instances: int, multi_knapsack_instances: int,
                      traveling_salesman_instances: int):
    dataset = {}
    sc = set_cover(
        n_problems=set_cover_instances,
        sets=(100, 300),
        elements=(50, 400),
    )
    dataset['SC'] = sc

    # bp = bin_packing(
    #     n_problems=bin_packing_instances,
    #     items=(10, 24),
    #     bins=(5, 12),
    #     bin_capacity=(50, 100),
    #     item_size=(10, 60),
    # )
    bp = bin_packing(
        n_problems=bin_packing_instances,
        items=(10, 20),
        bins=(5, 10),
        bin_capacity=(0.5, 1.5),
        item_size=(0.1, 0.9),
    )
    dataset['BP'] = bp

    mkp = multi_knapsack(
        n_problems=multi_knapsack_instances,
        items=(15, 75),
        knapsacks=(1, 5),
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
