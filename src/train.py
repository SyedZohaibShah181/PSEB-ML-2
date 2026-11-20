# Syed Zohaib Shah, PSEB-2026-010729, 2026-11-22
"""Part B: End-to-end tabular ML baseline for Online Retail.

Target: is_high_value_order (1 if invoice total > median, else 0).

Leaking columns EXCLUDED from features:
  - InvoiceNo, StockCode, Description (identifiers/free text)
  - InvoiceDate parts used only for engineered features, not raw
  - Quantity, UnitPrice (used to compute target — MUST exclude raw)
  - Any per-invoice aggregate that reconstructs the target
"""
import json
import pathlib
import warnings

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLEANED = ROOT / "data" / "cleaned" / "online_retail_cleaned.csv"
REPORTS = ROOT / "outputs" / "reports"
MODELS = ROOT / "models"
REPORTS.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42


# ---------------------------------------------------------------
# 1. Load + build target (one row per InvoiceNo)
# ---------------------------------------------------------------
def load_and_build_target(path: pathlib.Path) -> pd.DataFrame:
    """Load cleaned data, aggregate to one row per invoice, build target."""
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    required = {"InvoiceNo", "Quantity", "UnitPrice", "InvoiceDate",
                "Country", "CustomerID"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["line_value"] = df["Quantity"] * df["UnitPrice"]

    # Aggregate per invoice
    invoice = (
        df.groupby("InvoiceNo")
          .agg(
              order_total=("line_value", "sum"),
              n_lines=("StockCode", "nunique"),
              total_quantity=("Quantity", "sum"),
              avg_unit_price=("UnitPrice", "mean"),
              max_unit_price=("UnitPrice", "max"),
              n_countries=("Country", "nunique"),
              customer=("CustomerID", "first"),
              country=("Country", "first"),
              invoice_month=("InvoiceDate", lambda s: s.iloc[0].month),
              invoice_dow=("InvoiceDate", lambda s: s.iloc[0].dayofweek),
              invoice_hour=("InvoiceDate", lambda s: s.iloc[0].hour),
          )
          .reset_index()
    )

    threshold = invoice["order_total"].median()
    invoice["is_high_value_order"] = (invoice["order_total"] > threshold).astype(int)
    print(f"Threshold (median order_total): {threshold:.2f}")
    print(f"Positive class share: {invoice['is_high_value_order'].mean():.3f}")

    return invoice


# ---------------------------------------------------------------
# 2. Feature list — NO leaks
# ---------------------------------------------------------------
FEATURE_COLS_NUM = [
    "n_lines", "total_quantity", "avg_unit_price", "max_unit_price",
    "n_countries", "invoice_month", "invoice_dow", "invoice_hour",
]
FEATURE_COLS_CAT = ["country"]
TARGET = "is_high_value_order"
# Explicitly excluded (leak or identifier):
LEAK_COLS = ["order_total", "InvoiceNo", "customer"]


# ---------------------------------------------------------------
# 3. Build preprocessing pipeline
# ---------------------------------------------------------------
def build_preprocessor() -> ColumnTransformer:
    num_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("num", num_pipe, FEATURE_COLS_NUM),
        ("cat", cat_pipe, FEATURE_COLS_CAT),
    ])


# ---------------------------------------------------------------
# 4. Split BEFORE any fitting
# ---------------------------------------------------------------
def split_data(invoice: pd.DataFrame):
    X = invoice[FEATURE_COLS_NUM + FEATURE_COLS_CAT]
    y = invoice[TARGET]
    # Stratified random split — justified in docs/assumptions.md
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Train rows: {len(X_train)}, Test rows: {len(X_test)}")
    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------------
# 5. Models to compare
# ---------------------------------------------------------------
MODELS_DICT = {
    "dummy":      DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE),
    "logreg":     LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
    "rf":         RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE),
    "gb":         GradientBoostingClassifier(random_state=RANDOM_STATE),
}


def compare_models(X_train, y_train) -> pd.DataFrame:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
        "pr_auc": "average_precision",
    }
    rows = []
    for name, clf in MODELS_DICT.items():
        pipe = Pipeline([("pre", build_preprocessor()), ("clf", clf)])
        scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring)
        rows.append({
            "model": name,
            "precision": scores["test_precision"].mean(),
            "recall": scores["test_recall"].mean(),
            "f1": scores["test_f1"].mean(),
            "roc_auc": scores["test_roc_auc"].mean(),
            "pr_auc": scores["test_pr_auc"].mean(),
        })
        print(f"  {name}: f1={rows[-1]['f1']:.3f} roc_auc={rows[-1]['roc_auc']:.3f}")
    return pd.DataFrame(rows).sort_values("f1", ascending=False)


# ---------------------------------------------------------------
# 6. Fit best on full train, evaluate ONCE on test
# ---------------------------------------------------------------
def final_eval(model_name, X_train, y_train, X_test, y_test):
    clf = MODELS_DICT[model_name]
    pipe = Pipeline([("pre", build_preprocessor()), ("clf", clf)])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1]

    metrics = {
        "model": model_name,
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "pr_auc": float(average_precision_score(y_test, y_proba)),
    }
    print("\nTest metrics:", json.dumps(metrics, indent=2))
    print("\nConfusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nClassification report:\n",
          classification_report(y_test, y_pred, digits=3))

    joblib.dump(pipe, MODELS / "pipeline.joblib")
    (REPORTS / "test_metrics.json").write_text(json.dumps(metrics, indent=2))

    # ---- Build a DataFrame with BOTH full test rows AND predictions ----
    test_df = X_test.copy().reset_index(drop=True)
    test_df["y_true"] = y_test.reset_index(drop=True).values
    test_df["y_pred"] = y_pred
    test_df["y_proba"] = y_proba

    # Save ALL test rows (useful for full error analysis)
    test_df.to_csv(REPORTS / "test_predictions.csv", index=False)

    # Save ONLY misclassified rows for error analysis
    errors = test_df[test_df["y_true"] != test_df["y_pred"]].copy()
    errors.to_csv(REPORTS / "errors.csv", index=False)
    print(f"\nSaved ALL {len(test_df)} test rows to test_predictions.csv")
    print(f"Saved {len(errors)} misclassified rows to errors.csv")
    return metrics


# ---------------------------------------------------------------
# 7. Main
# ---------------------------------------------------------------
def main():
    print("=== Loading cleaned data and building target ===")
    invoice = load_and_build_target(CLEANED)
    invoice.to_csv(REPORTS / "invoice_level_dataset.csv", index=False)

    print("\n=== Splitting (train/test) BEFORE fitting ===")
    X_train, X_test, y_train, y_test = split_data(invoice)

    print("\n=== Cross-validated model comparison on TRAIN only ===")
    comparison = compare_models(X_train, y_train)
    comparison.to_csv(REPORTS / "model_comparison.csv", index=False)
    print("\n", comparison.to_string(index=False))

    best = comparison.iloc[0]["model"]
    print(f"\n=== Fitting best model ({best}) and evaluating on TEST set ONCE ===")
    final_eval(best, X_train, y_train, X_test, y_test)

    print("\nDone. Artifacts saved to models/ and outputs/reports/")


if __name__ == "__main__":
    main()
