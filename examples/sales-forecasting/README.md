# Sales Forecasting — datalab Worked Example

A small, real, end-to-end project used both as a demo of the `datalab` plugin and as a
smoke-test fixture for the plugin's own test suite. Companion to
`examples/iris-classification` — same worked-example shape, applied to a **time-series**
task instead of classification.

## What's here

```
sales-forecasting/
├── README.md               # this file
├── config.yaml              # seed, task type, target/date columns, data path
├── data/
│   └── sales.csv             # 72-row deterministic synthetic monthly sales series (seed 42)
├── src/sales_ts/
│   ├── __init__.py
│   └── forecast.py            # chronological split + lag features + LinearRegression vs seasonal-naive
└── EXPECTED.md              # expected result, for smoke-checking
```

## The task

Forecast next month's `sales` from its own recent history: a `lag_1` feature (last month's
value), a `lag_12` feature (same month one year prior), and a raw calendar-`month` indicator.
`config.yaml` pins `task_type: time-series`, `target: sales`, `date_column: date`, and
`seed: 42` for reproducibility.

`data/sales.csv` is **synthetic**, generated deterministically (`numpy.random.default_rng(42)`)
with a clear linear upward trend, a repeating 12-month seasonal cycle (peaks every December,
troughs every June), and mild Gaussian noise on top — 72 monthly rows, 2019-01 through
2024-12.

## Reproduce it with datalab

This folder is intentionally already scaffolded, so the fastest way to explore it with the
plugin is to treat it as an **existing** project:

```
cd examples/sales-forecasting
/datalab:work
```

`/datalab:work` will detect the existing `config.yaml`, `data/`, and `src/` layout (there's
no `.datalab/state.json` yet, so it reconstructs state from what it finds on disk), profile
`data/sales.csv`, and propose next steps.

Run the full experiment end-to-end (chronological split, lag-feature engineering, fit,
evaluate against the seasonal-naive baseline, plots, conclusions):

```
/datalab:run
```

Generate documentation and deliverables (report, deck, model/data cards) once results exist:

```
/datalab:docs
```

You can also run the forecasting script directly, without the plugin, to sanity-check the
data and pipeline:

```
python -m pip install pandas numpy scikit-learn
python src/sales_ts/forecast.py
```

**Result (this run):** `LinearRegression` on `lag_1 + lag_12 + month` scores **MAE 4.98 /
RMSE 6.50** on the last 12 held-out months, versus **MAE 28.79 / RMSE 29.81** for a
seasonal-naive (t-12) baseline over the same window — see `EXPECTED.md` for the full numbers
and how to reproduce them.

## Notes

- **This is a proper backtest, not an in-sample fit — there is no leakage from the future.**
  The split is chronological: the last 12 months are held out as test and everything before
  is train, in date order, never shuffled. `sklearn.model_selection.train_test_split(...,
  shuffle=True)` (used in `examples/iris-classification`, where it is correct for iid tabular
  rows) would be a leakage bug here — shuffling would routinely let the model train on rows
  that come *after* the ones it is evaluated on, i.e. train on the future and get graded on
  the past. `forecast.py` never does this; see its module docstring and
  `chronological_split()` for the full reasoning, and `train_and_evaluate()` for why the
  lag features used in the test window are not leakage either (they only ever reference
  already-observed, earlier months).
- Lag features (`lag_1`, `lag_12`) are built with `.shift()` on the full chronologically
  sorted series *before* the train/test split, so every lag value only ever references a
  genuinely earlier month. The first 12 rows of the series (which have no 12-months-ago value
  yet) are dropped outright, not imputed.
- `month` is fed in as a raw 1-12 integer rather than one-hot encoded — a deliberate
  simplification to stay within core deps (pandas/numpy/scikit-learn) and a single linear
  model. One-hot month dummies, or a sin/cos cyclical encoding, would be the natural next
  step if extending this example.
- `data/sales.csv` is fully synthetic and reproducible (seed 42), not a real business's sales
  — it's meant to be a fast, readable fixture with unambiguous trend + seasonality, not a
  benchmark dataset.
