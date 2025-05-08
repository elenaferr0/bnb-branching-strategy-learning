from dataset.sources.problems.bin_packing import bin_packing
from dataset.sources.problems.set_cover import set_cover
from dataset.sources.problems.traveling_salesman import traveling_salesman

def generate_datasets(set_cover_instances: int, bin_packing_instances: int, traveling_salesman_instances: int):
    dataset = {}
    sc = set_cover(
        n_problems=set_cover_instances,
        universe_size_range=(50, 80),
    )
    dataset['SC'] = sc

    bp = bin_packing(
        n_problems=bin_packing_instances,
        items=(7, 10),
        bins=(4, 8),
        bin_capacity=(70, 120),
        item_size=(10, 50),
    )
    bp = bin_packing(
        n_problems=bin_packing_instances,
        items=(10, 20),
        bins=(5, 10),
        bin_capacity=(0.5, 1.5),
        item_size=(0.1, 0.9),
    )
    dataset['BP'] = bp

    tsp = traveling_salesman(
        n_problems=traveling_salesman_instances,
        cities=(6, 15),
    )
    dataset['TSP'] = tsp

    return dataset