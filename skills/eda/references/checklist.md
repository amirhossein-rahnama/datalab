# EDA checklist

Work through in order; skip only what's genuinely not applicable to the task type, and say
so in the findings summary rather than silently omitting it.

## 1. Structure
- [ ] Shape (rows × columns)
- [ ] Dtypes per column — flag anything that should be numeric/datetime but loaded as object
- [ ] First/last few rows sanity check (not just `.head()` — look for obvious garbage)

## 2. Missingness
- [ ] Missing % per column
- [ ] Missingness pattern — random vs structured (e.g., missing together, missing by group)
- [ ] Any column >50% missing — candidate for drop, note it, don't drop yet

## 3. Duplicates
- [ ] Exact duplicate rows
- [ ] Duplicate keys (if an ID column exists) — should be unique unless it's expected

## 4. Target / class balance (modeling task types)
- [ ] Target distribution (histogram for regression; class counts for classification)
- [ ] Imbalance ratio — flag if worse than ~1:4, this blocks "accuracy" as the eval metric
      later (see `skills/verify/references/model-quality.md`)
- [ ] For time-series: is the target stationary? Any obvious trend/seasonality?

## 5. Univariate
- [ ] Distribution per numeric feature (histogram/KDE) — note skew, multi-modality
- [ ] Value counts per categorical feature — note high-cardinality columns (candidate for
      target/hash encoding rather than one-hot)

## 6. Bivariate / correlation
- [ ] Correlation heatmap (numeric features) — flag near-duplicate features (|r| > 0.95)
- [ ] Feature-vs-target relationship for top candidate features
- [ ] **Leakage screen**: any feature with near-perfect correlation with the target, or that
      couldn't be known at prediction time (post-outcome timestamp, a field derived from the
      target) — flag explicitly, don't just note the correlation

## 7. Outliers
- [ ] IQR or z-score flag per numeric column
- [ ] Decide per flagged column: plausible extreme value vs data error — note, don't drop

## 8. Task-specific
- [ ] **Time-series**: datetime parsing correct, sort order, gaps in the time index, sampling
      frequency, seasonality plot
- [ ] **NLP**: text length distribution, vocabulary size, language, obvious encoding issues
- [ ] **Computer vision**: image count/class, resolution consistency, corrupt-file scan,
      channel/colorspace sanity check
- [ ] **Recommendation**: user/item count, interaction sparsity, cold-start prevalence

## 9. Output
- [ ] `reports/data_dictionary.md` written (see SKILL.md Step 4)
- [ ] Figures saved to `reports/figures/`, not left inline-only in the notebook
- [ ] Findings summary cell: shape, task-type confirmation, class balance verdict, top data
      issues, and an explicit recommendation for `modeling`
