"""First pass at the customer/order data.

This is intentionally kept small while the dataset and column definitions are being checked.
"""

import pandas as pd

DATA_PATH = "data/orders.csv"


def inspect_data(path: str) -> None:
    df = pd.read_csv(path)
    print("shape:", df.shape)
    print("\ncolumns:")
    print(df.columns.tolist())
    print("\nmissing values:")
    print(df.isna().sum().sort_values(ascending=False).head(15))
    print("\ndtypes:")
    print(df.dtypes)


if __name__ == "__main__":
    inspect_data(DATA_PATH)
