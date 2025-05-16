import os

from datetime import datetime
import pandas as pd
from tqdm import tqdm
import numpy as np

from sources.generator import generate_datasets
from sources.miplib import load_miplib_dataset
from sources.tsplib import load_tsplib_dataset
from dataset.sources.perso import load_perso

current_dir = os.path.dirname(os.path.abspath(__file__))

def solve(problems, name):
    if len(problems) == 0:
        return

    dataset_name = f"{current_dir}/{name}_solution.pkl"
    stats_name = f"{current_dir}/{name}_stats.pkl"

    dataset = pd.read_pickle(dataset_name) if os.path.exists(dataset_name) else pd.DataFrame()
    stats = pd.read_pickle(stats_name) if os.path.exists(stats_name) else pd.DataFrame()

    for problem in tqdm(problems, desc=f"Solving problems {name}", unit="problem"):
        # try:
        names = stats['name'].values if stats.get('name', None) is not None else []
        if not problem.name in names:
            solution, stats_result = problem.solve_with_sb()
            dataset = pd.concat([dataset, solution], ignore_index=True)
            stats_row  = pd.DataFrame.from_dict(stats_result, orient='index').T
            stats = pd.concat([stats, stats_row], ignore_index=True)
            print(f"Problem {problem.name} solved in {stats_result['time']} seconds")
            # overwrite dataset and stats files
            dataset.to_pickle(f"{current_dir}/{name}_solution.pkl")
            stats.to_pickle(f"{current_dir}/{name}_stats.pkl")
        else:
            print(f"Problem {problem.name} already solved, skipping.")
        # except AssertionError as e:
        #     print(f"Problem has no solution: {problem.name}")
        # except Exception as e:
        #     print(f"Error solving problem {problem.name}: {e}")
        #     continue

def export_generated():
    generated = generate_datasets(
        set_cover_instances=0,
        bin_packing_instances=60,
        traveling_salesman_instances=0,
    )

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

def export_miplib():
    miplib = load_miplib_dataset()

    for problem in miplib:
        print(f"Solving {problem.name} problem {datetime.now()}")
        solve([problem], "miplib")

    # sort miplib problems by size (number of variables)
    miplib.sort(key=lambda x: len(x.c), reverse=True)

    for problem in tqdm(miplib, desc="Solving miplib problems", unit="problem"):
        print(f"Solving {problem.name} problem {datetime.now()}")
        solve([problem], "miplib")

def export_tsplib():
    tsplib = load_tsplib_dataset()
    for problem in tqdm(tsplib, desc="Solving tsplib problems", unit="problem"):
        print(f"Solving {problem.name} problem {datetime.now()}")
        solve([problem], "tsplib")
    
def export_perso():
    perso = load_perso()
    for problem in tqdm(perso, desc="Solving perso problems", unit="problem"):
        print(f"Solving {problem.name} problem {datetime.now()}")
        solve([problem], "perso")

if __name__ == "__main__":
    np.random.seed(42)
    # export_generated()
    # export_miplib()
    # export_tsplib()
    export_perso()

