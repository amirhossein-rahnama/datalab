#!/usr/bin/env python3
"""Time series utilities: chronological (never-shuffled) train/test splitting, three
baseline forecasters (naive, seasonal-naive, moving-average), and forecast error metrics.

Only core deps (pandas, numpy) are used, all importable at module scope.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def chronological_split(df, test_size, date_col=None):
    """Split `df` into (train, test) preserving row order -- never shuffles.

    If `date_col` is given, `df` is sorted by it (ascending) first; otherwise `df` is
    assumed to already be in chronological order. `test_size` is either a fraction
    (0 < test_size < 1) or an absolute row count (int >= 1) held out as the trailing test
    set.
    """
    if date_col is not None:
        df = df.sort_values(date_col)

    n = len(df)
    if isinstance(test_size, float):
        n_test = int(round(n * test_size))
    else:
        n_test = int(test_size)
    n_test = max(0, min(n, n_test))
    n_train = n - n_test

    train_df = df.iloc[:n_train]
    test_df = df.iloc[n_train:]
    return train_df, test_df


def naive_forecast(series, horizon) -> np.ndarray:
    """Persistence baseline: repeat the last observed value `horizon` times."""
    values = np.asarray(series, dtype=float)
    if values.size == 0:
        raise ValueError("series must not be empty")
    return np.full(horizon, values[-1], dtype=float)


def seasonal_naive_forecast(series, horizon, season) -> np.ndarray:
    """Repeat the last full seasonal cycle (last `season` observations), tiled to cover
    `horizon` steps: forecast[h] = series[-season + (h mod season)].
    """
    values = np.asarray(series, dtype=float)
    if season <= 0:
        raise ValueError("season must be a positive integer")
    if values.size < season:
        raise ValueError("series must have at least `season` observations")
    last_season = values[-season:]
    reps = int(np.ceil(horizon / season))
    return np.tile(last_season, reps)[:horizon]


def moving_average_forecast(series, horizon, window) -> np.ndarray:
    """Repeat the trailing moving average (mean of the last `window` observations)
    `horizon` times.
    """
    values = np.asarray(series, dtype=float)
    if window <= 0:
        raise ValueError("window must be a positive integer")
    if values.size < window:
        raise ValueError("series must have at least `window` observations")
    avg = float(values[-window:].mean())
    return np.full(horizon, avg, dtype=float)


def forecast_metrics(y_true, y_pred) -> dict:
    """MAE, RMSE, and MAPE (percent) between true and forecast values.

    MAPE is computed only over points where `y_true` != 0 (undefined otherwise); if every
    `y_true` value is 0, MAPE is NaN.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    errors = y_true - y_pred

    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))

    nonzero = y_true != 0
    if np.any(nonzero):
        mape = float(np.mean(np.abs(errors[nonzero] / y_true[nonzero])) * 100.0)
    else:
        mape = float("nan")

    return {"mae": mae, "rmse": rmse, "mape": mape}
