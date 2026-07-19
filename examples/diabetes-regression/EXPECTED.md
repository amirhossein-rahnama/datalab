# Expected Result

Running `python src/diabetes_reg/train.py` (or `/datalab:run` against this project) trains a
`StandardScaler → Ridge` pipeline with `seed=42` on an 80/20 train/test split of the 442-row
`data/diabetes.csv` (scikit-learn's built-in "diabetes" dataset) and should achieve **R2 ≈
0.45 on the held-out test set**, comfortably ahead of a `DummyRegressor(strategy="mean")`
baseline fit on the identical split. `seed=42` is fixed everywhere the split and the model use
randomness (`train_test_split(..., random_state=42)` and `Ridge(random_state=42)`), so
re-running `train.py` unmodified reproduces the numbers below exactly.

Smoke threshold: treat any run scoring **R2 < 0.40** on the held-out test set, or scoring at
or below the Dummy baseline's R2, as a smoke-check failure worth investigating (a broken
train/test split, a leakage bug, or a corrupted `data/diabetes.csv`) rather than as normal
model variance. This dataset is noisy — ten baseline variables predicting a one-year disease
progression score — so R2 well above ~0.55 on a single 80/20 split would itself be a little
suspicious (check for a leakage bug before celebrating).

## Measured output (reference run)

```
Train rows: 353 | Test rows: 89

Ridge (StandardScaler + Ridge, seed=42):
  R2:   0.4541
  RMSE: 53.7775

DummyRegressor(strategy='mean') baseline:
  R2:   -0.0120
  RMSE: 73.2225
```

The Ridge pipeline explains about 45% of the test-set variance in disease progression; the
mean-only baseline explains essentially none (a negative R2 means it does slightly worse on
this particular test split than a horizontal line at the *training* mean would on its own
data — expected behavior for `strategy="mean"`, not a bug). RMSE drops from 73.22 (baseline)
to 53.78 (Ridge), roughly a 27% reduction in typical prediction error.
