import pandas as pd

bp = pd.read_pickle("./SC_train_stats.pkl")
print(bp.tail(10))