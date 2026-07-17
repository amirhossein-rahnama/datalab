# Model-quality gate — detailed rubric

Heuristics for `scripts/diagnostics.py` / `scripts/explain.py` output. Treat thresholds as
defaults to reason from, not absolute law — a genuinely tiny/noisy dataset changes what's
plausible.

## Overfitting

- Train score substantially higher than validation/CV score (rule of thumb: gap > ~10
  percentage points on a bounded metric like accuracy/F1, or train R² notably higher than CV
  R² for regression) → flag overfitting.
- Learning curve: validation score plateaus or worsens while train score keeps climbing as
  more data/capacity is added → overfitting signal even if the current gap looks small.
- Fix direction: regularization, simpler model, more data, fewer/selected features (inside
  the pipeline, not by peeking at test data).

## Underfitting

- Both train and validation scores are poor **and** close to each other, and close to (or
  worse than) the baseline → underfitting, not "just a hard problem" until baseline
  comparison rules that out.
- Fix direction: more expressive model, better features, less aggressive regularization.

## Leakage

- **Target leakage**: a feature suspiciously highly correlated with the target, or one
  `eda`'s data dictionary already flagged as post-outcome. Cross-check explainability output
  — if the top SHAP/importance feature is the flagged one, that's confirmation, not just a
  coincidence.
- **Preprocessing-fit leakage**: any evidence that scaling/imputation/encoding was fit
  outside the CV loop (e.g., suspiciously perfect CV consistency across folds, or code
  inspection shows `.fit()` called on the full dataset before `train_test_split`/CV).
- **Temporal leakage**: for time-series, confirm the CV splitter is `TimeSeriesSplit` or
  equivalent — plain shuffled k-fold on temporal data is an automatic fail.
- **Near-duplicate leakage**: train/test overlap from augmentation or repeated entities —
  check whether a `GroupKFold`/entity-aware split was needed and used.
- Any confirmed leakage is a **hard fail** — the reported metric is not trustworthy until
  fixed, no matter how good it looks.

## CV rigor

- CV strategy matches the task (see `skills/modeling/references/task-recipes.md`).
- Fold count reasonable for dataset size (too few folds on a small dataset → high-variance
  estimate; note this rather than silently trusting a k=3 result on 150 rows).
- Score spread across folds is reported, not just the mean. A **very tight** spread on a
  small/noisy dataset is itself suspicious (possible leakage); a **very wide** spread means
  the point estimate alone is not a reliable claim.

## Class imbalance

- Flag if the minority class is below ~20% (rule of thumb, adjust by domain).
- If flagged, plain accuracy as the *headline* metric is a fail — require F1/PR-AUC/balanced
  accuracy (or whichever the task recipe recommends) to be the reported number instead.

## Metric appropriateness

- Classification on imbalanced data reporting only accuracy → fail (see above).
- Regression reporting only R² with no error-scale metric (RMSE/MAE) → fail; R² alone hides
  scale and can mislead on non-linear-fit cases.
- Any metric choice that's misaligned with the stated business/research question (e.g.,
  optimizing recall when the cost of a false positive is what actually matters) → flag for
  the user, not a silent pass.

## Baseline

- The candidate model must beat the Dummy/naive baseline on the primary metric, on the same
  CV protocol. If it doesn't: hard fail — a model that doesn't beat Dummy is not a model, it's
  noise with extra steps.

## Error analysis

- Confusion matrix deep-dive (which classes are confused with which, not just overall
  accuracy).
- Worst-case examples: the N highest-loss / most-confidently-wrong predictions, inspected for
  a pattern (data quality issue vs genuine model limitation vs leakage artifact).
- Failure slices: does error concentrate in a particular subgroup/segment/time range? This
  overlaps with the fairness check below but is broader (any slice, not just protected
  attributes).

## Model-comparison leaderboard

- At least 2 real candidates (beyond Dummy) were actually compared under the same protocol —
  a "leaderboard" with one row is a fail on this check specifically, independent of whether
  that one model is good.

## Explainability

- SHAP values / feature importances / partial dependence exist and are sane: the important
  features are plausible given domain knowledge and don't point back at a leakage feature.
- For deep/black-box models where SHAP is expensive, a documented fallback (permutation
  importance) is acceptable — absence of any explainability output is not.

## Fairness

- Subgroup performance breakdown across any column that looks like a protected/sensitive
  attribute (from the data dictionary — demographic-like columns, or any column the user
  flags as sensitive).
- Flag meaningful performance gaps across subgroups (e.g., recall differs by >10pp between
  groups) even if not required to fix by policy — surface it, let the user/domain decide.
- This feeds the model card's fairness section in `document` regardless of outcome — "no
  concerning gap found" is itself a reportable finding, not a skip.
