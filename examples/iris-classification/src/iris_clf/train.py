"""Train a leakage-safe Logistic Regression classifier on the Iris worked example.

Pipeline: StandardScaler -> LogisticRegression, wrapped in a single sklearn Pipeline so the
scaler is fit only on the training split. No statistics from the held-out test rows leak into
preprocessing.

Usage:
    python src/iris_clf/train.py
    python src/iris_clf/train.py --data data/iris.csv --seed 42 --test-size 0.3
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42
FEATURE_COLUMNS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
TARGET_COLUMN = "species"
DEFAULT_TEST_SIZE = 0.3
# examples/iris-classification/src/iris_clf/train.py -> examples/iris-classification/data/iris.csv
DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "iris.csv"


def load_data(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the Iris CSV into a DataFrame."""
    return pd.read_csv(path)


def build_pipeline(seed: int = SEED) -> Pipeline:
    """Leakage-safe pipeline: StandardScaler + LogisticRegression fit together, train-only."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=seed)),
        ]
    )


def train_and_evaluate(
    df: pd.DataFrame, seed: int = SEED, test_size: float = DEFAULT_TEST_SIZE
) -> tuple[Pipeline, float]:
    """Split, fit the pipeline on the training split only, and score on the held-out test split."""
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=seed,
        stratify=y,
    )

    pipeline = build_pipeline(seed=seed)
    pipeline.fit(X_train, y_train)  # scaler + classifier both fit on X_train only

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Train rows: {len(X_train)} | Test rows: {len(X_test)}")
    print(f"Accuracy: {accuracy:.4f}")
    print()
    print(classification_report(y_test, y_pred))

    return pipeline, accuracy


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train the Iris StandardScaler + LogisticRegression pipeline."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to iris.csv (default: examples/iris-classification/data/iris.csv)",
    )
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed (default: 42)")
    parser.add_argument(
        "--test-size",
        type=float,
        default=DEFAULT_TEST_SIZE,
        help="Held-out test fraction (default: 0.3)",
    )
    args = parser.parse_args()

    df = load_data(args.data)
    train_and_evaluate(df, seed=args.seed, test_size=args.test_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
