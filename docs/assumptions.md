# Assumptions, Limitations, Risks

## Part A — Data Quality Pipeline

### Assumptions
- Raw file is authoritative; we never modify `data/raw/`.
- GBP is the implicit currency of `UnitPrice`.
- Quantity and UnitPrice follow typical retail distributions; values beyond 1.5× IQR are anomalies.
- CustomerID null = unidentifiable customer; we treat these as out of scope.

### Limitations
- IQR filtering can discard genuine bulk orders (e.g. wholesale). Documented, not "fixed".
- Date-based effects (holidays, promotions) not modelled in Part A; only cleaned.
- Country spellings: only stripped/lowercased; no fuzzy matching to ISO codes.
- No currency conversion — cross-country revenue comparisons assume GBP.

### What we chose not to fix (and why)
- Cancellations (InvoiceNo starting with "C") were removed as outliers via negative Quantity; we did not build a separate returns dataset. Simpler for Part B.
- Missing CustomerID: we drop rather than impute. Imputation would invent identities that don't exist.
- Extreme UnitPrice values: removed. Could be legitimate — documented as a risk.

### Data-quality metrics
See `outputs/reports/data_quality.md`
### Features that mattered most (permutation importance, F1)
Top features: <feat1> >> <feat2> >> <feat3>.
Makes sense because <one-sentence reason>.
Full list: `outputs/reports/permutation_importance.csv`.

### Error patterns found
See `outputs/reports/error_analysis.md` for detail. Summary:
- ...


### Features that mattered most (permutation importance, F1)

| Feature | Mean importance |
|---|---|
| total_quantity | 0.442 |
| avg_unit_price | 0.118 |
| max_unit_price | 0.007 |
| n_lines | 0.005 |
| invoice_month | 0.0004 |

**Makes sense:** the target is a function of `Quantity × UnitPrice`, so the two aggregates that approximate those terms dominate. Country, hour, day-of-week, and month contribute essentially nothing — plausible for a UK-dominated dataset with a fixed business definition of "high value".

### Error patterns found (see `outputs/reports/error_analysis.md`)

- **Overall error rate: 6.1%** (204 / 3,366 test rows), consistent with F1 = 0.94.
- **Error concentrates in mid-size baskets (4–100 lines).** Single-line and 100+ baskets are error-free.
- **Two concrete patterns:**
  1. *False negative:* many cheap items (33 lines, avg £1.25) → model predicts low value but total exceeded the median.
  2. *False positive:* high line count (44 lines) makes the model predict high value, but low average price means the actual total falls short.
- **Country and hour are not error drivers.**

### Features with near-zero importance (v2 candidates to drop)

- `invoice_hour`, `invoice_month`, `invoice_dow` — near-zero permutation importance. Removing them simplifies the model without loss of F1.