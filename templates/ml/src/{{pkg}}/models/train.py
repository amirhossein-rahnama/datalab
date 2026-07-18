"""Model training for {{project}} - leakage-safe sklearn Pipeline skeleton.

All preprocessing (imputation, scaling, encoding) lives INSIDE the Pipeline so
it is fit only on training folds during cross-validation - never on the full
dataset before splitting. Swap the DummyClassifier for a real estimator once
you have features; check Context7 for current sklearn API before extending.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from {{pkg}}.config import SEED  # noqa: E402

NUMERIC_FEATURES: list[str] = []  # TODO: fill in numeric column names
CATEGORICAL_FEATURES: list[str] = []  # TODO: fill in categorical column names


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ]
    )


def build_pipeline(estimator) -> Pipeline:
    """Wrap any estimator with the shared leakage-safe preprocessor."""
    return Pipeline(steps=[("preprocess", build_preprocessor()), ("model", estimator)])


def train(X, y, estimator=None):
    """Fit + cross-validate. Replace `estimator` with a real model before use.

    Defaults to a DummyClassifier so this skeleton runs end-to-end out of the
    box - every real model must beat this baseline (see verify skill).
    """
    if estimator is None:
        estimator = DummyClassifier(strategy="stratified", random_state=SEED)

    pipeline = build_pipeline(estimator)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    scores = cross_validate(pipeline, X, y, cv=cv, scoring="accuracy", return_estimator=True)
    print(f"[train] cv accuracy: {scores['test_score'].mean():.4f} +/- {scores['test_score'].std():.4f}")

    pipeline.fit(X, y)
    return pipeline, scores


if __name__ == "__main__":
    print("[train] TODO: load data and call train(X, y, estimator) - this is a skeleton.")
