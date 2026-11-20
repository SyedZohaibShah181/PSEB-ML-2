# Your Name, Roll Number, 2026-11-18
import pandas as pd
import pytest

from src.validation import check_no_nulls, check_range, check_types, check_unique


def test_check_no_nulls_pass():
    check_no_nulls(pd.DataFrame({"a": [1, 2]}), ["a"])

def test_check_no_nulls_fails():
    with pytest.raises(ValueError):
        check_no_nulls(pd.DataFrame({"a": [1, None]}), ["a"])

def test_check_range_pass():
    check_range(pd.DataFrame({"q": [1, 5, 100]}), "q", 0, 100)

def test_check_range_fails():
    with pytest.raises(ValueError):
        check_range(pd.DataFrame({"q": [-5, 3]}), "q", 0, 100)

def test_check_unique_pass():
    check_unique(pd.DataFrame({"id": [1, 2, 3]}), "id")

def test_check_unique_fails():
    with pytest.raises(ValueError):
        check_unique(pd.DataFrame({"id": [1, 1, 2]}), "id")

def test_check_types_pass():
    check_types(pd.DataFrame({"a": [1, 2]}), {"a": "int64"})

def test_check_types_fails():
    with pytest.raises(ValueError):
        check_types(pd.DataFrame({"a": [1, 2]}), {"a": "float64"})