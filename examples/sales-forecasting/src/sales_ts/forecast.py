"""Forecast monthly sales with lag features + LinearRegression, backtested against a
seasonal-naive baseline, for the datalab sales-forecasting worked example.

WHY THIS LOOKS DIFFERENT FROM examples/iris-classification/src/iris_clf/train.py
----------------------------------------------------------------------------------
Time-series ML breaks one habit that's completely safe for iid tabular data: random
splitting. `sklearn.model_selection.train_test_split(shuffle=True)` (used in the Iris
example) assumes every row is exchangeable — row order carries no information, so assigning
rows to train/test at random is fine. That assumption is FALSE for a time series: row order
*is* the information. A random or shuffled split would let the model train on, say,
December 2024 while being "tested" on June 2022 — i.e. it trains on the future and gets
graded on the past. That leaks information no real forecaster would have (at prediction
time for June 2022, December 2024 hasn't happened yet) and produces a score that looks great
in development and then falls apart in production, where you only ever have data up to
"now". The fix used throughout this file is a **chronological holdout**: sort by date, take
the last N months as test, everything before as train, and never shuffle.

Usage:
    python src/sales_ts/forecast.py
    python src/sales_ts/forecast.py --data data/sales.csv --seed 42 --test-months 12
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# examples/sales-forecasting/src/sales_ts/forecast.py -> examples/sales-forecasting/src
# Robustly makes `sales_ts` importable (as a package, e.g. from a test or notebook) whether
# this file is run directly, via `python -m`, or imported elsewhere — no editable install
# needed. Mirrors the sys.path pattern used by the plugin's own templates
# (templates/base/pipeline.py, templates/ml/src/{{pkg}}/models/train.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from sales_ts import __version__  # noqa: E402  (import after sys.path setup, see above)

SEED = 42
# LinearRegression's fit is a deterministic least-squares solve (no `random_state` param, no
# shuffling anywhere in this pipeline), so SEED has no numerical effect today. It's threaded
# through the config/CLI anyway for interface parity with train.py and in case a future
# swap-in estimator (e.g. GradientBoostingRegressor, SGDRegressor) needs it.
DATE_COLUMN = "date"
TARGET_COLUMN = "sales"
DEFAULT_TEST_MONTHS = 12
LAG_COLUMNS = ["lag_1", "lag_12"]
# `month` is fed in as a raw 1-12 integer, not one-hot encoded. That's a real simplification
# (it implies December=12 and January=1 are "far apart" numerically, even though they're
# adjacent in the yearly cycle) made to keep this example to core deps + a plain
# LinearRegression. One-hot month dummies (or sin/cos encoding) would be the natural next
# step — see README.md "Notes".
FEATURE_COLUMNS = LAG_COLUMNS + ["month"]
# examples/sales-forecasting/src/sales_ts/forecast.py -> examples/sales-forecasting/data/sales.csv
DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sales.csv"


def load_data(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the sales CSV and sort chronologically.

    Sorting by date is not cosmetic: every function below (lag features, the chronological
    split) assumes row order == time order. If the CSV ever arrives out of order, skipping
    this line would silently corrupt both the lags and the split.
    """
    df = pd.read_csv(path, parse_dates=[DATE_COLUMN])
    df = df.sort_values(DATE_COLUMN).reset_index(drop=True)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lag-1, lag-12, and a calendar-month feature.

    `.shift()` only ever reads *earlier* rows of the already-sorted frame, so lag_1[t] and
    lag_12[t] are always values that had genuinely already happened by month t — there is no
    way for this line to leak a future value into a feature. Rows without a full lag history
    (the first 12 months of the series have no month-12-ago value yet) are dropped outright
    rather than imputed with a placeholder, so the model never trains on a made-up lag.
    """
    out = df.copy()
    out["lag_1"] = out[TARGET_COLUMN].shift(1)
    out["lag_12"] = out[TARGET_COLUMN].shift(12)
    out["month"] = out[DATE_COLUMN].dt.month
    out = out.dropna(subset=LAG_COLUMNS).reset_index(drop=True)
    return out


def chronological_split(
    df: pd.DataFrame, test_months: int = DEFAULT_TEST_MONTHS
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into train/test by date order, NOT randomly.

    The test set is always the most recent `test_months` rows of the (already sorted) frame.
    This mirrors how the model will actually be used: fit on everything known so far,
    forecast the months that haven't happened yet.

    Contrast with `train_test_split(..., shuffle=True)` in the Iris example: shuffling
    assigns rows to train/test independently of time, which for a time series means the
    model would routinely train on months *after* the ones it's being tested on. That is a
    correctness bug, not a style choice — it inflates the score during development and the
    gap shows up the moment the model faces genuinely unseen, not-yet-happened data.
    """
    if test_months >= len(df):
        raise ValueError(f"test_months={test_months} must be smaller than {len(df)} available rows")
    train = df.iloc[:-test_months].reset_index(drop=True)
    test = df.iloc[-test_months:].reset_index(drop=True)
    return train, test


def seasonal_naive_forecast(test: pd.DataFrame) -> np.ndarray:
    """Baseline: predict this month's sales as *last year's same month's* sales (lag-12).

    This is the standard first baseline for a seasonal series (see
    skills/modeling/references/task-recipes.md: "time-series -> Seasonal-naive baseline...").
    No fitting, no parameters — just "assume this year rhymes with last year." A model earns
    its extra complexity only if it beats this on the same held-out rows.
    """
    return test["lag_12"].to_numpy()


def train_and_evaluate(
    df: pd.DataFrame, seed: int = SEED, test_months: int = DEFAULT_TEST_MONTHS
) -> dict:
    """Fit on the training window only, forecast the held-out test window, and score both
    the model and the seasonal-naive baseline on the same rows.

    A note on why the test-window lag features are NOT leakage: lag_1/lag_12 for every test
    row are computed once via `.shift()` on the full chronologically-sorted series *before*
    the split (see `build_features`), and they only ever reference 1 and 12 months *earlier*
    than that row — actual, already-observed sales figures. By the time month t needs a
    forecast, months t-1 and t-12 have already happened in the real world, so using them is
    legitimate. This is a one-step-ahead backtest, not a recursive multi-step forecast (which
    would instead feed the model's own prior *predictions* back in as the next month's
    lag_1). Either way, nothing at or after month t is used to predict month t, and the
    model's coefficients are fit ONLY on `train` — the test window never touches `.fit()`.
    """
    featured = build_features(df)
    train, test = chronological_split(featured, test_months=test_months)

    X_train, y_train = train[FEATURE_COLUMNS], train[TARGET_COLUMN]
    X_test, y_test = test[FEATURE_COLUMNS], test[TARGET_COLUMN]

    model = LinearRegression()
    model.fit(X_train, y_train)  # fit on the chronological training window ONLY
    y_pred = model.predict(X_test)

    baseline_pred = seasonal_naive_forecast(test)

    model_mae = mean_absolute_error(y_test, y_pred)
    model_rmse = mean_squared_error(y_test, y_pred) ** 0.5
    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    baseline_rmse = mean_squared_error(y_test, baseline_pred) ** 0.5

    test_dates = test[DATE_COLUMN].dt.strftime("%Y-%m")
    print(f"sales_ts v{__version__}")
    print(f"Train rows: {len(train)} | Test rows: {len(test)} (last {test_months} months)")
    print(f"Test window: {test_dates.iloc[0]} .. {test_dates.iloc[-1]} (chronological, not shuffled)")
    print()
    print(f"{'Model':<32}{'MAE':>10}{'RMSE':>10}")
    print(f"{'LinearRegression (lag+month)':<32}{model_mae:>10.3f}{model_rmse:>10.3f}")
    print(f"{'Seasonal-naive (t-12) baseline':<32}{baseline_mae:>10.3f}{baseline_rmse:>10.3f}")
    print()
    beats_baseline = model_mae <= baseline_mae
    verdict = "beats" if model_mae < baseline_mae else "ties"
    if not beats_baseline:
        verdict = "LOSES TO"
    print(f"Result: LinearRegression {verdict} the seasonal-naive baseline on MAE.")

    return {
        "train_rows": len(train),
        "test_rows": len(test),
        "model_mae": model_mae,
        "model_rmse": model_rmse,
        "baseline_mae": baseline_mae,
        "baseline_rmse": baseline_rmse,
        "beats_baseline": beats_baseline,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Forecast sales with a lag-feature LinearRegression vs a seasonal-naive baseline."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to sales.csv (default: examples/sales-forecasting/data/sales.csv)",
    )
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed (default: 42)")
    parser.add_argument(
        "--test-months",
        type=int,
        default=DEFAULT_TEST_MONTHS,
        help="Number of most-recent months held out as the test window (default: 12)",
    )
    args = parser.parse_args()

    df = load_data(args.data)
    results = train_and_evaluate(df, seed=args.seed, test_months=args.test_months)

    # Smoke assertion: a model that can't match a naive "repeat last year" heuristic isn't
    # earning its keep (see skills/verify/references/model-quality.md, "Baseline": a candidate
    # that doesn't beat the naive baseline is a hard fail, not a model). We warn rather than
    # hard-exit non-zero so the script stays useful for exploration with unusual
    # --test-months values, but the intended contract for this dataset+seed is: beats/ties.
    if not results["beats_baseline"]:
        print("WARNING: model did not beat the seasonal-naive baseline on MAE.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
