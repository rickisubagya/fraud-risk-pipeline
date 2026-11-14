from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.config import get_engine

engine = get_engine()

df = pd.read_csv(Path("data/raw/creditcard.csv"))
df.columns = [c.lower() for c in df.columns]
df.insert(0, "transaction_id", range(1, len(df) + 1))

transactions = df[["transaction_id", "time", "amount"]].rename(
    columns={"time": "time_seconds"}
)
features = df[["transaction_id"] + [f"v{i}" for i in range(1, 29)]]
labels = pd.DataFrame(
    {"transaction_id": df["transaction_id"], "is_fraud": df["class"].astype(bool)}
)

schema_sql = Path("sql/schema.sql").read_text()

with engine.begin() as conn:
    conn.execute(text(schema_sql))
    conn.execute(
        text("TRUNCATE fraud_labels, transaction_features, transactions RESTART IDENTITY")
    )
    for name, table in [
        ("transactions", transactions),
        ("transaction_features", features),
        ("fraud_labels", labels),
    ]:
        table.to_sql(name, conn, if_exists="append", index=False,
                     method="multi", chunksize=5000)
    conn.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('transactions', 'transaction_id'), "
            "(SELECT MAX(transaction_id) FROM transactions))"
        )
    )

with engine.connect() as conn:
    for name in ["transactions", "transaction_features", "fraud_labels"]:
        print(name, conn.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar())