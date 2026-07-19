# Expected Result

Running `python src/sales_ts/forecast.py` (or `/datalab:run` against this project) loads
`data/sales.csv`, sorts it chronologically, engineers `lag_1` / `lag_12` / `month` features
(dropping the first 12 rows, which have no 12-months-ago value yet), splits off the **last 12
months as a chronological test window** — 2024-01 through 2024-12, with the preceding 48
months (2020-01 through 2023-12) as train, in date order, **never shuffled** — fits a plain
`LinearRegression` on the training window only, and forecasts the held-out window.

## Measured result (this run)

```
sales_ts v0.1.0
Train rows: 48 | Test rows: 12 (last 12 months)
Test window: 2024-01 .. 2024-12 (chronological, not shuffled)

Model                                  MAE      RMSE
LinearRegression (lag+month)         4.981     6.496
Seasonal-naive (t-12) baseline      28.790    29.812

Result: LinearRegression beats the seasonal-naive baseline on MAE.
```

| Model                                    |    MAE |   RMSE |
|-------------------------------------------|-------:|-------:|
| `LinearRegression` (`lag_1`+`lag_12`+`month`) |  4.981 |  6.496 |
| Seasonal-naive baseline (value from t-12)  | 28.790 | 29.812 |

Exit code: `0`.

## Smoke assertion

The model **should beat or match the seasonal-naive baseline** on the held-out window
(`model_mae <= baseline_mae`) — a model that cannot even match "assume this year repeats
last year" is not earning its extra complexity (see
`skills/verify/references/model-quality.md`, "Baseline": failing to beat the naive baseline
is a hard fail, not normal variance).

On this seed/dataset it clearly does, by a wide margin: MAE drops from **28.79 -> 4.98**
(roughly a 5.8x reduction), and RMSE from **29.81 -> 6.50**. This gap is expected, not
suspicious: the synthetic series (see `data/sales.csv`, generated with
`numpy.random.default_rng(42)`) has a steady linear upward trend on top of its 12-month
seasonal cycle. The seasonal-naive baseline only ever looks exactly 12 months back, so it
has no way to see the trend and systematically *undershoots* by roughly a year's worth of
trend growth (~12 months x ~2.5 units/month ≈ 30, which is why its MAE lands close to 28.79).
`lag_1` (recent momentum) plus `month` (seasonal offset) let the linear model pick up both
the trend and the seasonal cycle that the baseline misses.

Treat any run that **loses to the baseline**, or that deviates far from the numbers above at
the pinned seed (`seed: 42` in `config.yaml`, `numpy.random.default_rng(42)` in the data
generator), as a smoke-check failure worth investigating — most likely a broken chronological
split (e.g. shuffling crept back in), a lag-feature leakage bug, or a corrupted
`data/sales.csv` — rather than as normal model variance. (`LinearRegression`'s fit is a
deterministic least-squares solve on a fixed CSV, so re-running this script should reproduce
the exact numbers above bit-for-bit, not just "close.")
