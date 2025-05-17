import os

from datetime import datetime
import pandas as pd
from tqdm import tqdm
import numpy as np

from problem import Problem

current_dir = os.path.dirname(os.path.abspath(__file__))

def solve(problems, name):
    if len(problems) == 0:
        return

    dataset_name = f"{current_dir}/{name}_solution.pkl"
    stats_name = f"{current_dir}/{name}_stats.pkl"

    dataset = pd.read_pickle(dataset_name) if os.path.exists(dataset_name) else pd.DataFrame()
    stats = pd.read_pickle(stats_name) if os.path.exists(stats_name) else pd.DataFrame()

    for problem in tqdm(problems, desc=f"Solving problems {name}", unit="problem"):
        try:
            names = stats['name'].values if stats.get('name', None) is not None else []
            if not problem.name in names:
                solution, stats_result = problem.solve_with_sb(logged=True)
                dataset = pd.concat([dataset, solution], ignore_index=True)
                stats_row  = pd.DataFrame.from_dict(stats_result, orient='index').T
                stats = pd.concat([stats, stats_row], ignore_index=True)
                print(f"Problem {problem.name} solved in {stats_result['time']} seconds")
                # overwrite dataset and stats files
                dataset.to_pickle(f"{current_dir}/{name}_solution.pkl")
                stats.to_pickle(f"{current_dir}/{name}_stats.pkl")
            else:
                print(f"Problem {problem.name} already solved, skipping.")
        except AssertionError as e:
            print(f"Problem has no solution: {problem.name}")
        except Exception as e:
            print(f"Error solving problem {problem.name}: {e}")
            continue

def bin_packing(n_problems: int, items: (int, int), bins: (int, int), bin_capacity: (float, float),
                item_size: (float, float)):
    return [__generate_problem(i, items, bins, bin_capacity, item_size) for i in range(n_problems)]


def __generate_problem(id: int, items: (int, int), bins: (int, int), bin_capacity: (float, float),
                       item_size: (float, float)):
    n_items = np.random.randint(*items)
    n_bins = np.random.randint(*bins)
    bin_capacity = np.random.uniform(*bin_capacity)
    item_sizes = np.random.uniform(*item_size, size=n_items)
    n_vars = n_bins + n_items * n_bins  # y_i + x_{ij}
    assert n_vars < 1000, "Community edition has a limit of 1000 variables"

    c = np.concatenate([
        np.ones(n_bins),  # cost for bins (y_j)
        np.zeros(n_items * n_bins)  # no cost for x_{ij} (multiplying n_items * n_bins as x has 2 indexes)
    ])

    A, b, types = [], [], []

    ## constraints
    # k >= 1
    A.append(np.concatenate([np.zeros(n_bins), np.ones(n_items * n_bins)]))
    b.append(1)
    types.append('G')

    # sum(s(i) * x_ij) <= B * y_j for all j
    for j in range(n_bins):
        row = np.zeros(n_vars)
        row[j] = -bin_capacity  # coefficient for y_j
        for i in range(n_items):
            row[n_bins + i * n_bins + j] = item_sizes[i]  # coefficient for x_{ij}
        A.append(row)
        b.append(0)
        types.append('L')

    # sum(x_ij) = 1 for all i
    for i in range(n_items):
        row = np.zeros(n_vars)
        for j in range(n_bins):
            row[n_bins + i * n_bins + j] = 1  # coefficient for x_{ij}
        A.append(row)
        b.append(1)
        types.append('E')

    A = np.array(A)
    b = np.array(b)
    assert A.shape[0] == b.shape[0], "A and b must have the same number of rows"
    assert b.shape[0] <= 1000, "Community edition has a limit of 1000 constraints"

    types = np.array(types)

    return Problem(
        name=f"random_BP_{id}",
        c=c,
        lb=[0] * n_vars,
        ub=[1] * n_vars,
        constraint_types=types,
        b=b,
        A=A
    )

def set_cover(n_problems: int, universe_size_range=(50, 70), seed=None):
    if seed is not None:
        np.random.seed(seed)

    return [__generate_sc(i, universe_size_range) for i in range(n_problems)]


def __generate_sc(id: int, universe_size_range):
    # universe selection
    universe_size = np.random.randint(*universe_size_range)
    universe = np.random.choice(list(range(1, 100)), size=universe_size, replace=False)

    binary_matrix = np.random.randint(0, 2, size=(len(universe), len(universe)))

    # Ensure each row and column has at least one 1 to avoid empty sets
    for i in range(binary_matrix.shape[0]):
        if np.sum(binary_matrix[i, :]) == 0:
            binary_matrix[i, np.random.randint(0, binary_matrix.shape[1])] = 1

    for j in range(binary_matrix.shape[1]):
        if np.sum(binary_matrix[:, j]) == 0:
            binary_matrix[np.random.randint(0, binary_matrix.shape[0]), j] = 1

    # mapping to universe elements
    subsets = []
    for j in range(binary_matrix.shape[1]):
        subset = []
        for i in range(binary_matrix.shape[0]):
            if binary_matrix[i, j] == 1:
                subset.append(universe[i])
        subsets.append(subset)

    # remove duplicated sets from subsets
    unique_subsets = []
    for subset in subsets:
        if subset not in unique_subsets:
            unique_subsets.append(subset)

    # shuffling within subsets
    for i in range(len(unique_subsets)):
        np.random.shuffle(unique_subsets[i])

    # Create Problem object
    n_subsets = len(unique_subsets)
    n_elements = len(universe)

    A = np.zeros((n_elements, len(unique_subsets)))
    for j, subset in enumerate(unique_subsets):
        for elem in subset:
            i, = np.where(universe == elem)
            A[i, j] = 1

    c = np.ones(len(unique_subsets))
    b = np.ones(n_elements)
    types = ['G'] * n_elements

    return Problem(
        name=f"SC_{id}",
        c=c,
        lb=[0] * n_subsets,
        ub=[1] * n_subsets,
        constraint_types=types,
        b=b,
        A=A,
    )

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


def export_generated():
    generated = generate_datasets(
        set_cover_instances=60,
        bin_packing_instances=00,
        traveling_salesman_instances=0,
    )


    del generated['BP']

    # split in train and test (80% train, 20% test)
    for name, problems in generated.items():
        n_train = int(len(problems) * 0.8)
        np.random.shuffle(problems)
        generated[name] = {
            'train': problems[:n_train],
            'test': problems[n_train:]
        }

    for name, problems in generated.items():
        print(f"Solving {name} problems")
        solve(problems['train'], f"{name}_train")
        print(f"Solving {name} test problems")
        solve(problems['test'], f"{name}_test")

if __name__ == "__main__":
    np.random.seed(42)
    export_generated()
    # export_miplib()
    # export_tsplib()
    # export_perso()

