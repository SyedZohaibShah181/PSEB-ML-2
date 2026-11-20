# Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20
"""Load cleaned data into SQLite and run a GROUP BY query."""
import os
import sqlite3

import pandas as pd

CLEANED = "data/cleaned/online_retail_cleaned.csv"
DB = "sql/retail.db"

def main():
    os.makedirs("sql", exist_ok=True)
    os.makedirs("outputs/reports", exist_ok=True)

    df = pd.read_csv(CLEANED, parse_dates=["InvoiceDate"])
    con = sqlite3.connect(DB)
    df.to_sql("sales", con, if_exists="replace", index=False)

    # Query 1: top 10 countries by revenue (Quantity * UnitPrice)
    query = """
    SELECT Country,
           COUNT(*)                         AS n_transactions,
           SUM(Quantity * UnitPrice)        AS total_revenue
    FROM sales
    GROUP BY Country
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    result = pd.read_sql(query, con)
    print("--- Top 10 Countries by Revenue ---")
    print(result)
    result.to_csv("outputs/reports/top_countries_revenue.csv", index=False)

    # Query 2 (join example): revenue per month (derived table + join)
    query2 = """
    SELECT strftime('%Y-%m', InvoiceDate) AS month,
           SUM(Quantity * UnitPrice)      AS revenue,
           COUNT(DISTINCT Country)        AS n_countries
    FROM sales
    GROUP BY month
    ORDER BY month;
    """
    result2 = pd.read_sql(query2, con)
    print("\n--- Monthly Revenue Summary ---")
    print(result2)
    result2.to_csv("outputs/reports/monthly_revenue.csv", index=False)

    con.close()
    print(f"\nSQLite DB written to {DB}")
    print("Results saved to outputs/reports/")

if __name__ == "__main__":
    main()
