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
|-- notebooks/
|   `-- 02_analysis.ipynb
|-- outputs/
|   |-- figures/
|   `-- reports/
|       |-- data_quality.md
|       |-- monthly_revenue.csv
|       `-- top_countries_revenue.csv
|-- sql/
|   |-- analysis.sql
|   `-- retail.db
|-- src/
|   |-- cleaning.py
|   |-- inspect_data.py
|   |-- load_sqlite.py
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
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Data Quality Pipeline & Database Load

```powershell
# Run unit tests
pytest

# Load cleaned data into SQLite and run SQL reports
python src/load_sqlite.py
```
