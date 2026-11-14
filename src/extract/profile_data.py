from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/raw/creditcard.csv")

df = pd.read_csv(DATA_PATH)

print("Rows, Columns:", df.shape)
print("Columns:", df.columns.tolist())
print("Total missing values:", df.isnull().sum().sum())
print(df["Class"].value_counts())
print("Fraud ratio: {:.4%}".format(df["Class"].mean()))