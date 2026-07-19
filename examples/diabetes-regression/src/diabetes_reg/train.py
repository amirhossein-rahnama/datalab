"""Train a leakage-safe Ridge Regression model on the Diabetes worked example.

Pipeline: StandardScaler -> Ridge, wrapped in a single sklearn Pipeline so the scaler is fit
only on the training split. No statistics from the held-out test rows leak into preprocessing.

Also fits a DummyRegressor(strategy="mean") baseline on the same train/test split, so the
Ridge pipeline's R2 can be judged against "always predict the training-set mean" rather than
in isolation.

Usage:
    python src/diabetes_reg/train.py
    python src/diabetes_reg/train.py --data data/diabetes.csv --seed 42 --test-size 0.2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Put `src/` on sys.path so `diabetes_reg` is importable no matter what directory this script
# is invoked from (running it directly, via `/datalab:run`, or from a notebook). Mirrors the
# sys.path convention used elsewhere in this plugin (templates/base/pipeline.py,
# templates/base/tests/test_smoke.py).
_SRC_DIR = Path(__file__).resolve().parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42
FEATURE_COLUMNS = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
TARGET_COLUMN = "target"
DEFAULT_TEST_SIZE = 0.2
# examples/diabetes-regression/src/diabetes_reg/train.py -> examples/diabetes-regression/data/diabetes.csv
DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "diabetes.csv"


def load_data(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the Diabetes CSV into a DataFrame."""
    return pd.read_csv(path)


def build_pipeline(seed: int = SEED) -> Pipeline:
    """Leakage-safe pipeline: StandardScaler + Ridge fit together, train-only."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("reg", Ridge(random_state=seed)),
        ]
    )


def train_and_evaluate(
    df: pd.DataFrame, seed: int = SEED, test_size: float = DEFAULT_TEST_SIZE
) -> tuple[Pipeline, float, float]:
    """Split, fit the pipeline on the training split only, and score on the held-out test split.

    Also fits a `DummyRegressor(strategy="mean")` baseline on the identical split, purely for
    comparison — it never leaks into the Ridge pipeline's own fit or predictions.

    Returns (fitted_pipeline, r2, rmse) for the Ridge pipeline on the test split.
    """
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=seed,
    )

    pipeline = build_pipeline(seed=seed)
    pipeline.fit(X_train, y_train)  # scaler + regressor both fit on X_train only

    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)
    baseline_pred = baseline.predict(X_test)
    baseline_r2 = r2_score(y_test, baseline_pred)
    baseline_rmse = float(np.sqrt(mean_squared_error(y_test, baseline_pred)))

    print(f"Train rows: {len(X_train)} | Test rows: {len(X_test)}")
    print()
    print(f"Ridge (StandardScaler + Ridge, seed={seed}):")
    print(f"  R2:   {r2:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print()
    print("DummyRegressor(strategy='mean') baseline:")
    print(f"  R2:   {baseline_r2:.4f}")
    print(f"  RMSE: {baseline_rmse:.4f}")

    return pipeline, r2, rmse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train the Diabetes StandardScaler + Ridge pipeline."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to diabetes.csv (default: examples/diabetes-regression/data/diabetes.csv)",
    )
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed (default: 42)")
    parser.add_argument(
        "--test-size",
        type=float,
        default=DEFAULT_TEST_SIZE,
        help="Held-out test fraction (default: 0.2)",
    )
    args = parser.parse_args()

    df = load_data(args.data)
    train_and_evaluate(df, seed=args.seed, test_size=args.test_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
