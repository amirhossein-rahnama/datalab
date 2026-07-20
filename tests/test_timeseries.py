import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import timeseries  # noqa: E402


def test_chronological_split_keeps_order_with_date_col():
    df = pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=20, freq="D"),
        "value": np.arange(20),
    })
    shuffled = df.sample(frac=1.0, random_state=1).reset_index(drop=True)

    train_df, test_df = timeseries.chronological_split(shuffled, test_size=0.2, date_col="date")

    assert len(train_df) == 16
    assert len(test_df) == 4
    assert train_df["date"].max() < test_df["date"].min()
    assert train_df["date"].is_monotonic_increasing
    assert test_df["date"].is_monotonic_increasing


def test_chronological_split_no_shuffle_without_date_col():
    df = pd.DataFrame({"value": np.arange(20)})
    train_df, test_df = timeseries.chronological_split(df, test_size=5)

    assert list(train_df["value"]) == list(range(15))
    assert list(test_df["value"]) == list(range(15, 20))


def test_seasonal_naive_beats_naive_on_clean_seasonal_series():
    rng = np.random.RandomState(0)
    t = np.arange(120)
    season = 12
    seasonal_pattern = 10 * np.sin(2 * np.pi * t / season)
    series = 50 + seasonal_pattern + rng.normal(scale=0.5, size=120)

    horizon = 12
    y_true = series[-horizon:]
    train_series = series[:-horizon]

    naive_pred = timeseries.naive_forecast(train_series, horizon)
    seasonal_pred = timeseries.seasonal_naive_forecast(train_series, horizon, season)

    naive_metrics = timeseries.forecast_metrics(y_true, naive_pred)
    seasonal_metrics = timeseries.forecast_metrics(y_true, seasonal_pred)

    assert seasonal_metrics["mae"] < naive_metrics["mae"]


def test_moving_average_forecast_matches_trailing_mean():
    series = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    forecast = timeseries.moving_average_forecast(series, horizon=3, window=3)
    assert forecast.shape == (3,)
    assert np.allclose(forecast, np.mean(series[-3:]))


def test_forecast_metrics_keys_and_perfect_prediction():
    y_true = [10.0, 20.0, 30.0]
    result = timeseries.forecast_metrics(y_true, y_true)
    assert set(result) == {"mae", "rmse", "mape"}
    assert result["mae"] == 0.0
    assert result["rmse"] == 0.0
    assert result["mape"] == 0.0
