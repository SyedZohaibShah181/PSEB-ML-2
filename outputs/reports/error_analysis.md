<!-- Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20 -->
# Error Analysis — Online Retail ML Baseline

**Model:** Gradient Boosting (best of 4 models, 5-fold stratified CV)
**Test set:** 3,366 invoices (20% holdout, used exactly once)
**Total errors:** 204 / 3,366 = **6.1% error rate**

## Test set metrics

| Metric | Value |
|---|---|
| Precision | 0.932 |
| Recall | 0.948 |
| F1 | 0.940 |
| ROC-AUC | 0.987 |
| PR-AUC | 0.987 |

## Error rate by basket size

| Bucket | n rows | Error rate |
|---|---|---|
| 1 | 224 | 0.0% |
| 2-3 | 279 | 1.1% |
| 4-10 | 846 | 7.4% |
| 11-100 | 1,986 | 6.9% |
| 100+ | 31 | 0.0% |

**Pattern:** Errors concentrate in mid-size baskets (4-100 lines). Single-line and very large baskets are essentially error-free. The 4-100 range is where total value is genuinely ambiguous near the median threshold — a basket of 20 cheap items can land just under or just over. This is expected for a median-threshold classification problem.

## Error rate by country (n >= 10)

| Country | n | Error rate |
|---|---|---|
| Netherlands | 13 | 7.7% |
| United Kingdom | 3,021 | 6.2% |
| Germany | 85 | 5.9% |
| Switzerland | 17 | 5.9% |
| EIRE | 47 | 4.3% |

**Pattern:** UK dominates the test set; error rate aligns with overall 6.1%. Non-UK countries have small counts — any conclusions are weak. Model generalises across countries.

## Error rate by hour

Flat across business hours (8am-5pm). Consistent with `invoice_hour` having near-zero permutation importance (0.0004). Not a useful signal — candidate for removal in v2.

## Concrete failure patterns

### Pattern 1 — False negatives from low average unit price
**Example:** `n_lines=33, total_quantity=154, avg_unit_price=1.25, y_proba=0.18`
Model predicted low value because average price is low, but actual total exceeded the 195.98 median. Many slightly-priced items summed over the threshold. The model relies on `total_quantity` and `avg_unit_price` as proxies for the true total.

### Pattern 2 — False positives from high line count
**Example:** `n_lines=44, total_quantity=155, avg_unit_price=1.67, y_proba=0.74`
Model predicted high value because `n_lines` and `total_quantity` look large, but low average price meant actual total fell short. Model has no feature capturing the true line-value sum (that would be leakage).

## Limitations

1. All errors are near the decision boundary — intrinsic to the median-threshold framing.
2. No feature captures the true line-value sum (by design).
3. `invoice_hour`, `invoice_month`, `invoice_dow` contribute nothing.
4. Small countries (n < 20) cannot be evaluated reliably.

## Recommendations for v2

- Add `max_line_value` (highest single line total).
- Drop `invoice_hour`, `invoice_month`, `invoice_dow`.
- Group rare countries into `Other`.
- Re-tune threshold with a business cost matrix.

## Reproducibility

- Notebook: `notebooks/03_error_analysis.ipynb`
- All test predictions: `outputs/reports/test_predictions.csv`
- Misclassified rows: `outputs/reports/errors.csv`
- Permutation importances: `outputs/reports/permutation_importance.csv`
- Figures: `outputs/figures/error_by_basket_size.png`, `outputs/figures/proba_distribution.png`