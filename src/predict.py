# Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20
"""Part B: Batch prediction CLI for Online Retail ML pipeline."""
import argparse
import pathlib
import sys
import warnings

import joblib
import pandas as pd

warnings.filterwarnings("ignore")

# Ensure project root is in sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def predict_batch(model_path: str, input_path: str, output_path: str):
    m_path = pathlib.Path(model_path)
    in_path = pathlib.Path(input_path)
    out_path = pathlib.Path(output_path)

    print(f"Loading model from {m_path} ...")
    pipe = joblib.load(m_path)

    print(f"Reading input CSV: {in_path}")
    df = pd.read_csv(in_path)
    print(f"  {len(df)} rows, {df.shape[1]} columns")

    print("Running predictions ...")
    y_pred = pipe.predict(df)
    y_proba = pipe.predict_proba(df)[:, 1]

    out_df = df.copy()
    out_df["predicted_high_value"] = y_pred
    out_df["predicted_probability"] = y_proba

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    n_high = int((y_pred == 1).sum())
    pct_high = float((y_pred == 1).mean() * 100)
    print(f"Wrote {len(df)} predictions to {out_path}")
    print(f"  Predicted high-value: {n_high} rows ({pct_high:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Run batch predictions with trained pipeline.")
    parser.add_argument("--model", default="models/pipeline.joblib", help="Path to saved pipeline")
    parser.add_argument("--input", required=True, help="Path to input CSV with features")
    parser.add_argument("--output", required=True, help="Path to save output predictions CSV")
    args = parser.parse_args()

    predict_batch(args.model, args.input, args.output)


if __name__ == "__main__":
    main()
