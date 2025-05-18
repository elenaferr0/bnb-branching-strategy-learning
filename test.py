import pandas as pd

def convert():
    files = [
        "BP_train_solution.csv",
        "BP_test_solution.csv",
        "SC_train_solution.csv",
        "SC_test_solution.csv",
    ]

    for file in files:
        bp = pd.read_csv(file)
        bp = bp.drop(columns=["Unnamed: 0", "Unnamed: 0.1"])
        bp.to_pickle(file.replace(".csv", ".pkl"))

def pr():
    f = "BP_train_stats.pkl"
    bp = pd.read_pickle(f)
    print(bp.head(10))

if __name__ == "__main__":
    pr()