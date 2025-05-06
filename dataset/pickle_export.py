import os

import pandas as pd
from tqdm import tqdm
import numpy as np

from dataset import generate_datasets, load_miplib_dataset


def load_and_export():
    np.random.seed(42)
    dataset = pd.DataFrame()
    stats = pd.DataFrame()

    # miplib = load_miplib_dataset()
    problems = generate_datasets(
        set_cover_instances=0,
        bin_packing_instances=1,
        traveling_salesman_instances=1
    )
    for problem in problems['BP']:
        try:
            solution, stats_result = problem.solve()
            dataset = pd.concat([dataset, solution], ignore_index=True)
            stats_row  = pd.DataFrame.from_dict(stats_result, orient='index').T
            stats = pd.concat([stats, stats_row], ignore_index=True)
            print(f"Problem {problem.name} solved in {stats_result['time']} seconds")
        except Exception as e:
            print(f"Error in problem {problem.name}: {e}")

    if dataset.empty:
        return
    dataset.to_pickle(f'dataset.pickle')
    stats.to_pickle(f'stats.pickle')

if __name__ == "__main__":
    load_and_export()
