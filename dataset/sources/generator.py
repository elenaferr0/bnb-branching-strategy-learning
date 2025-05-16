from sources.problems.bin_packing import bin_packing
from sources.problems.set_cover import set_cover

def generate_datasets(set_cover_instances: int, bin_packing_instances: int, traveling_salesman_instances: int):
    dataset = {}
    dataset['SC'] = set_cover(
        n_problems=set_cover_instances,
        universe_size_range=(50, 80),
    )

    dataset['BP'] = bin_packing(
        n_problems=bin_packing_instances,
        items=(10, 20),
        bins=(5, 10),
        bin_capacity=(0.5, 1.5),
        item_size=(0.1, 0.9),
    )

    return dataset