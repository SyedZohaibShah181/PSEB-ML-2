# Syed Zohaib Shah, PSEB-2026-010729, 2026-11-20
"""Run reproducible end-to-end data cleaning and validation pipeline."""
import argparse
import os
import pathlib
import sys
import pandas as pd

# Ensure project root is in sys.path so 'src' can be imported regardless of execution cwd
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cleaning import parse_dates, remove_duplicates, handle_missing, remove_outliers
from src.validation import check_no_nulls, check_range


def clean_pipeline(input_path: str, output_path: str) -> pd.DataFrame:
    """Load raw data, clean, validate, and save output."""
    inp = pathlib.Path(input_path)
    out = pathlib.Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading raw data from {inp}...")
    if inp.suffix.lower() == ".xlsx":
        df = pd.read_excel(inp)
    else:
        df = pd.read_csv(inp)

    initial_rows = len(df)
    print(f"Initial raw rows: {initial_rows}")

    # 1. Parse dates
    df = parse_dates(df, "InvoiceDate")

    # 2. Remove duplicates
    df = remove_duplicates(df)

    # 3. Handle missing values
    df = handle_missing(df, {"CustomerID": "drop", "Description": "UNKNOWN"})

    # 4. Remove non-positive quantities and prices
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    # 5. Outlier removal using IQR
    df = remove_outliers(df, "Quantity", method="iqr")
    df = remove_outliers(df, "UnitPrice", method="iqr")

    # 6. Post-cleaning validation
    print("Running validation checks...")
    check_no_nulls(df, ["CustomerID", "Quantity", "UnitPrice", "Country", "InvoiceDate"])
    check_range(df, "Quantity", 1, df["Quantity"].max())
    check_range(df, "UnitPrice", 0.001, df["UnitPrice"].max())
    print("All validation checks passed 100%!")

    # 7. Save cleaned data
    df.to_csv(out, index=False)
    final_rows = len(df)
    print(f"Cleaned rows: {final_rows} (removed {initial_rows - final_rows}, {(initial_rows - final_rows)/initial_rows:.1%})")
    print(f"Saved cleaned data to {out}")

    return df


def main():
    parser = argparse.ArgumentParser(description="Run reproducible data cleaning pipeline.")
    parser.add_argument("--input", default="data/raw/online_retail.csv", help="Path to input raw data file")
    parser.add_argument("--output", default="data/cleaned/online_retail_cleaned.csv", help="Path to save cleaned data")
    args = parser.parse_args()

    clean_pipeline(args.input, args.output)


if __name__ == "__main__":
    main()
