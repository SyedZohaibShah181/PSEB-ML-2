# Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20
import pandas as pd
import pytest

from src.cleaning import (
    handle_missing,
    parse_dates,
    remove_duplicates,
    remove_outliers,
    standardize_categories,
)


def test_parse_dates_valid():
    df = pd.DataFrame({"d": ["2023-01-01", "2023-02-01"]})
    out = parse_dates(df, "d")
    assert out["d"].dtype.kind == "M"
    assert out["d"].isna().sum() == 0

def test_parse_dates_invalid_becomes_nat():
    df = pd.DataFrame({"d": ["not-a-date"]})
    out = parse_dates(df, "d")
    assert out["d"].isna().all()

def test_parse_dates_missing_col():
    with pytest.raises(KeyError):
        parse_dates(pd.DataFrame({"x": [1]}), "d")

def test_remove_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    out = remove_duplicates(df, ["a", "b"])
    assert len(out) == 2

def test_handle_missing_median():
    df = pd.DataFrame({"x": [1.0, None, 3.0]})
    out = handle_missing(df, {"x": "median"})
    assert out["x"].isna().sum() == 0
    assert out["x"].iloc[1] == 2.0

def test_handle_missing_drop():
    df = pd.DataFrame({"x": [1.0, None, 3.0]})
    out = handle_missing(df, {"x": "drop"})
    assert len(out) == 2

def test_remove_outliers_iqr():
    df = pd.DataFrame({"x": [1, 2, 2, 3, 100]})
    out = remove_outliers(df, "x")
    assert 100 not in out["x"].values

def test_standardize_categories():
    df = pd.DataFrame({"c": [" USA ", "usa", "Uk"]})
    out = standardize_categories(df, "c", {"usa": "USA", "uk": "UK"})
    # expected: ["USA", "USA", "Uk"] because original non-matching kept as-is after strip
    assert out["c"].iloc[0] == "USA"
    assert out["c"].iloc[1] == "USA"

def test_standardize_categories_missing_col():
    with pytest.raises(KeyError):
        standardize_categories(pd.DataFrame({"x": [1]}), "c", {})