import os

import pandas as pd
from tqdm import tqdm
import numpy as np

from dataset import generate_datasets, load_orlib_dataset


def load_and_export():
    # miplib_dataset = load_miplib_dataset()
    np.random.seed(42)

    # dataset = generate_datasets(
    #     set_cover_instances=1,
    #     bin_packing_instances=1,
    #     multi_knapsack_instances=0,
    #     traveling_salesman_instances=0
    # )
    # for problem in dataset['SC']:
    #     try:
    #         solution = problem.solve()
    #         break
    #         print(f"Problem {problem.name} solved with status: {solution.status}")
    #     except Exception as e:
    #         print(f"Error in problem {problem.name}: {e}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ds = load_orlib_dataset(os.path.join(current_dir, 'sources/orlib'))
    #
    df = pd.DataFrame()
    for problem in tqdm(ds, desc="Solving problems"):
        try:
            solution = problem.solve()
            df = pd.concat([df, solution], ignore_index=True)
            break
        except Exception as e:
            print(f"Error in problem {problem.name}: {e}")
    #
    # if df.empty:
    #     return
    # df.to_pickle(f'dataset.pickle')


if __name__ == "__main__":
    load_and_export()
