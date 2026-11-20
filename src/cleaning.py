# Name: Syed Zohaib Shah
# Roll Number: PSEB-2026-010729
# Date: 20-11-2026
# Project: Online Retail Data Inspection
import numpy as np
import pandas as pd


def parse_dates(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Parse date column to datetime; invalid values become NaT.
    Args: df, col (column name)
    Returns: new dataframe with parsed dates
    Raises: KeyError if column missing
    """
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found")
    out = df.copy()
    out[col] = pd.to_datetime(out[col], errors="coerce")
    return out

def remove_duplicates(df: pd.DataFrame, subset=None) -> pd.DataFrame:
    """Drop duplicate rows. Returns new dataframe."""
    return df.drop_duplicates(subset=subset, keep="first")

def handle_missing(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """strategy: {col: 'drop' | 'median' | 'mode' | <fill_value>}
    Returns: new dataframe with missing handled.
    """
    out = df.copy()
    for col, action in strategy.items():
        if col not in out.columns:
            raise KeyError(f"Column '{col}' not found")
        if action == "drop":
            out = out.dropna(subset=[col])
        elif action == "median":
            out[col] = out[col].fillna(out[col].median())
        elif action == "mode":
            out[col] = out[col].fillna(out[col].mode().iloc[0])
        else:
            out[col] = out[col].fillna(action)
    return out

def remove_outliers(df: pd.DataFrame, col: str, method: str = "iqr") -> pd.DataFrame:
    """Remove outliers using IQR (default) or z-score. Returns new df.
    For Online Retail: use on Quantity, UnitPrice to drop negatives/absurd values.
    """
    out = df.copy()
    if method == "iqr":
        q1, q3 = out[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        return out[(out[col] >= lo) & (out[col] <= hi)]
    elif method == "zscore":
        z = (out[col] - out[col].mean()) / out[col].std()
        return out[np.abs(z) <= 3]
    raise ValueError(f"Unknown method: {method}")

def standardize_categories(df: pd.DataFrame, col: str, mapping: dict) -> pd.DataFrame:
    """Map raw category values to canonical values.

    Values are stripped of whitespace and lowercased before lookup.
    Rows whose normalized value is not in `mapping` are kept as their
    stripped original (not lowercased) so case is preserved for unmapped values.

    Args:
        df: input dataframe
        col: column to standardize
        mapping: dict of {lowercase_raw: canonical_value}
    Returns:
        new dataframe with standardized column
    Raises:
        KeyError if col not in df
    """
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found")
    out = df.copy()
    stripped = out[col].astype(str).str.strip()
    normalized = stripped.str.lower()
    mapped = normalized.map(mapping)
    out[col] = mapped.fillna(stripped)
    return out