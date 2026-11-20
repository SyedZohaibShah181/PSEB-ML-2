# Name: Syed Zohaib Shah
# Roll Number: PSEB-2026-010729
# Date: 20-11-2026
# Project: Online Retail Data Inspection
import pandas as pd


def check_no_nulls(df: pd.DataFrame, cols: list[str]) -> None:
    """Raise ValueError if any of cols has nulls."""
    for c in cols:
        if c not in df.columns:
            raise KeyError(f"Column '{c}' not found")
        n = df[c].isna().sum()
        if n:
            raise ValueError(f"{n} nulls in column '{c}'")

def check_range(df: pd.DataFrame, col: str, lo, hi) -> None:
    """Raise if any value outside [lo, hi]."""
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found")
    bad = df[(df[col] < lo) | (df[col] > hi)]
    if len(bad):
        raise ValueError(f"{len(bad)} rows in '{col}' outside [{lo},{hi}]")

def check_types(df: pd.DataFrame, schema: dict) -> None:
    """Raise if column dtype doesn't match schema {'col': 'int64', ...}."""
    for col, expected in schema.items():
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found")
        if str(df[col].dtype) != expected:
            raise ValueError(f"'{col}' has {df[col].dtype}, expected {expected}")

def check_unique(df: pd.DataFrame, col: str) -> None:
    """Raise if column has duplicates."""
    if df[col].duplicated().any():
        raise ValueError(f"Duplicate values in '{col}'")