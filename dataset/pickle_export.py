import os

import pandas as pd
from tqdm import tqdm
import numpy as np

from dataset import generate_datasets, load_orlib_dataset, load_miplib_dataset


def load_and_export():
    np.random.seed(42)
    df = pd.DataFrame()

    dataset = load_miplib_dataset(size_limit=1)

    # dataset = generate_datasets(
    #     set_cover_instances=0,
    #     bin_packing_instances=1,
    #     multi_knapsack_instances=0,
    #     traveling_salesman_instances=0
    # )
    for problem in dataset:
        try:
            solution = problem.solve()
            break
            print(f"Problem {problem.name} solved with status: {solution.status}")
        except Exception as e:
            print(f"Error in problem {problem.name}: {e}")

    if df.empty:
        return
    df.to_pickle(f'dataset.pickle')


if __name__ == "__main__":
    load_and_export()
