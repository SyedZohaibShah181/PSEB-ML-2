<!-- Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20 -->
# Data Quality Report — Online Retail

## Source
- **URL:** https://archive.ics.uci.edu/dataset/352/online+retail
- **Licence:** CC BY 4.0
- **Access date:** 2026-11-15

## Before / After
| Metric | Raw | Cleaned | Change |
|---|---|---|---|
| Rows | 541,909 | 333,234 | removed 208,675 (38.5%) |
| Columns | 8 | 8 | preserved |
| Missing `CustomerID` | 135,080 | 0 | strategy: dropped |
| Missing `Description` | 1,454 | 0 | strategy: filled "UNKNOWN" |
| Exact duplicate rows | 5,268 | 0 | removed |
| Rows with Quantity ≤ 0 | 10,624 | 0 | rejected |
| Rows with UnitPrice ≤ 0 | 2,517 | 0 | rejected |
| Rows outside IQR for Quantity | 58,619 | 0 | removed |
| Rows outside IQR for UnitPrice | 39,627 | 0 | removed |
| Validation pass rate | — | 100% | all checks pass |

## Assumptions & what we did NOT fix
- **Negative Quantity:** These are returns/cancellations — we dropped them because the target is normal sales. Alternative: keep and model separately.
- **Missing `CustomerID` (~25%):** We drop these rows. They are still real sales, but cannot be tied to a customer, so they don't belong in customer-level modelling.
- **Negative UnitPrice:** Treated as data errors / free items; removed.
- **Currency:** All prices assumed to be GBP (the source's default). Not converted.
- **Date range:** Assumed the full range is valid; we did not trim weekends/holidays.
- **No imputation for missing UnitPrice:** if null after cleaning, rows are dropped — we did not model it as zero.

## Validation rules applied
- `Quantity > 0`
- `UnitPrice > 0`
- `CustomerID` not null
- `InvoiceDate` parses to datetime
- No exact duplicate rows
- `Country` is a non-empty string

## SQL result explanation
### Query Plan Output (`EXPLAIN QUERY PLAN`)
```text
SCAN sales
USE TEMP B-TREE FOR GROUP BY
USE TEMP B-TREE FOR ORDER BY
```
- **Query Execution:** SQLite executes a full table scan (`SCAN sales`), accumulates rows into a temporary B-Tree structure for the `GROUP BY Country` aggregation, and orders the grouped rows into another temporary B-Tree for `ORDER BY total_revenue DESC`.
- **Business Insight:** The query ranks countries by Quantity × UnitPrice; the UK contributes the vast majority of revenue, followed by long-tail countries.
