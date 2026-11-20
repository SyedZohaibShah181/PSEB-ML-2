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

## Model Card — Online Retail High-Value Order Classifier

**Model:** GradientBoostingClassifier inside a scikit-learn Pipeline
(`models/pipeline.joblib`).
**Task:** Binary classification — predict whether an invoice's total value
exceeds the median order total in the training data.
**Owner:** <Your Name>, <Roll Number>.
**Version:** v1 (2026-11-24).

**Intended use:**
Prioritise invoices for sales follow-up, fulfilment routing, or upsell
targeting — flag orders likely to be high-value so the business can act
before the order ships.

**Out of scope:**
- Credit scoring or customer-level risk assessment.
- Pricing or discount decisions.
- Predicting per-customer lifetime value.
- Any deployment on customer data not covered by the original licence.

**Inputs:** one row per invoice with:
`n_lines, total_quantity, avg_unit_price, max_unit_price, n_countries,
invoice_month, invoice_dow, invoice_hour, country`.

**Outputs:** `prediction` (0/1) and `proba_high_value` (float in [0, 1]).

**Performance:**
- Test F1 = 0.94, ROC-AUC = 0.987, PR-AUC = 0.987 (see `test_metrics.json`).
- Error rate 6.1%; errors concentrate in mid-size baskets near the median threshold.
- Full analysis: `outputs/reports/error_analysis.md`.

**Assumptions:**
- Threshold = median order value from the training period.
- Each invoice is one independent order.
- GBP is the implicit currency.

**Limitations:**
- No temporal holdout — may not generalise to a future season or new customer base.
- Small countries (n < 20 in test) cannot be evaluated reliably.
- Uses aggregate features only (no feature captures the true line-value sum, by design — that would be leakage).

**Risks:**
- Threshold drift: if the business definition of "high value" changes, the model must be retrained.
- Distribution shift: if product mix or pricing changes materially, error rate will rise.
- Model does NOT explain its predictions — decisions should be reviewed, not automated blindly.

**Monitoring (recommended):**
- Track precision/recall monthly against actual order values.
- Alert if predicted positive rate drifts more than ±10% from training baseline.
- Re-train when F1 drops below 0.85 on a fresh month.

**Inference:** `python src/predict.py --input <new.csv> --output <preds.csv>`