# Online Retail ML Project

This project inspects and prepares the Online Retail dataset for machine learning.

## SQL Analysis & Revenue Insights
The query ranks countries by Quantity × UnitPrice; the UK contributes the vast majority of revenue, followed by long-tail countries.

## Project structure

```text
Online_Retail_ML_Project/
|-- data/
|   |-- raw/
|   |   |-- Online Retail.xlsx
|   |   `-- online_retail.csv
|   `-- cleaned/
|       `-- online_retail_cleaned.csv
|-- docs/
|   `-- assumptions.md
|-- models/
|   `-- pipeline.joblib
|-- notebooks/
|   `-- 02_analysis.ipynb
|-- outputs/
|   |-- figures/
|   `-- reports/
|       |-- data_quality.md
|       |-- errors.csv
|       |-- invoice_level_dataset.csv
|       |-- model_comparison.csv
|       |-- monthly_revenue.csv
|       |-- test_metrics.json
|       `-- top_countries_revenue.csv
|-- sql/
|   |-- analysis.sql
|   `-- retail.db
|-- src/
|   |-- cleaning.py
|   |-- inspect_data.py
|   |-- load_sqlite.py
|   |-- run_pipeline.py
|   |-- train.py
|   `-- validation.py
|-- tests/
|   |-- test_cleaning.py
|   `-- test_validation.py
|-- requirements.txt
`-- README.md
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Reproducible Pipeline Execution

```powershell
# 1. Run unit tests
python -m pytest tests/ -v

# 2. Run reproducible data cleaning pipeline
python src/run_pipeline.py --input data/raw/online_retail.csv --output data/cleaned/online_retail_cleaned.csv

# 3. Load cleaned data into SQLite and run SQL reports
python src/load_sqlite.py

# 4. Train baseline tabular ML models and evaluate best model
python src/train.py
```
