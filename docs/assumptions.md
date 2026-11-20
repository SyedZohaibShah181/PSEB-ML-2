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
