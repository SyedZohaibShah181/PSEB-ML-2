# Tests for CLI and pipeline components
import pandas as pd

from src.load_sqlite import main as load_sqlite_main
from src.predict import main as predict_main
from src.run_pipeline import main as pipeline_main
from src.train import build_preprocessor, load_and_build_target


def test_predict_cli(tmp_path, monkeypatch):
    out_file = tmp_path / "preds.csv"
    monkeypatch.setattr(
        "sys.argv",
        ["predict.py", "--input", "data/raw/new_rows_sample.csv", "--output", str(out_file)]
    )
    predict_main()
    assert out_file.exists()
    df = pd.read_csv(out_file)
    assert len(df) == 20
    assert "y_pred" in df.columns


def test_run_pipeline_cli(tmp_path, monkeypatch):
    raw_csv = tmp_path / "raw.csv"
    out_csv = tmp_path / "cleaned.csv"
    sample_df = pd.DataFrame({
        "InvoiceNo": ["536365", "536366"],
        "StockCode": ["85123A", "71053"],
        "Description": ["WHITE HANGING HEART", "WHITE METAL LANTERN"],
        "Quantity": [6, 6],
        "InvoiceDate": ["2010-12-01 08:26:00", "2010-12-01 08:28:00"],
        "UnitPrice": [2.55, 3.39],
        "CustomerID": [17850.0, 17850.0],
        "Country": ["United Kingdom", "United Kingdom"],
    })
    sample_df.to_csv(raw_csv, index=False)
    monkeypatch.setattr(
        "sys.argv",
        ["run_pipeline.py", "--input", str(raw_csv), "--output", str(out_csv)]
    )
    pipeline_main()
    assert out_csv.exists()


def test_load_sqlite_cli(tmp_path, monkeypatch):
    db_file = tmp_path / "test_retail.db"
    rep_csv = tmp_path / "sample_cleaned.csv"
    sample_df = pd.DataFrame({
        "InvoiceNo": ["536365", "536366"],
        "StockCode": ["85123A", "71053"],
        "Description": ["WHITE HANGING HEART", "WHITE METAL LANTERN"],
        "Quantity": [6, 12],
        "InvoiceDate": ["2010-12-01 08:26:00", "2010-12-01 08:28:00"],
        "UnitPrice": [2.55, 3.39],
        "CustomerID": [17850.0, 17850.0],
        "Country": ["United Kingdom", "France"],
    })
    sample_df.to_csv(rep_csv, index=False)
    monkeypatch.setattr("src.load_sqlite.DB", str(db_file))
    monkeypatch.setattr("src.load_sqlite.CLEANED", str(rep_csv))
    load_sqlite_main()
    assert db_file.exists()


def test_train_helpers(tmp_path):
    pipe = build_preprocessor()
    assert pipe is not None

    mini_csv = tmp_path / "mini_cleaned.csv"
    sample_df = pd.DataFrame({
        "InvoiceNo": ["536365", "536365", "536366"],
        "StockCode": ["85123A", "71053", "22423"],
        "Description": ["A", "B", "C"],
        "Quantity": [6, 2, 10],
        "InvoiceDate": ["2010-12-01 08:26:00", "2010-12-01 08:26:00", "2010-12-02 10:00:00"],
        "UnitPrice": [2.55, 3.39, 1.25],
        "CustomerID": [17850.0, 17850.0, 13047.0],
        "Country": ["United Kingdom", "United Kingdom", "France"],
    })
    sample_df.to_csv(mini_csv, index=False)
    df = load_and_build_target(str(mini_csv))
    assert "is_high_value_order" in df.columns
    assert len(df) == 2
