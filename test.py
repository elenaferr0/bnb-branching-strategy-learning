import pandas as pd

def convert():
    files = [
        "dataset/exported/BP_train_solution.pkl",
        "dataset/exported/BP_test_solution.pkl",
        "dataset/exported/SC_train_solution.pkl",
        "dataset/exported/SC_test_solution.pkl",

        "dataset/exported/BP_train_stats.pkl",
        "dataset/exported/BP_test_stats.pkl",
        "dataset/exported/SC_train_stats.pkl",
        "dataset/exported/SC_test_stats.pkl",
    ]

    out = "dataset/exported_csv/"
    for file in files:
        bp = pd.read_pickle(file)
        bp.to_csv(out + file.split("/")[-1].replace(".pkl", ".csv"), index=False)

def pr():
    f = "./dataset/exported/BP_train_solution.pkl"
    bp = pd.read_pickle(f)
    print(bp.head(10))

if __name__ == "__main__":
    convert()