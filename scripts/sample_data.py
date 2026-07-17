#!/usr/bin/env python3
"""Synthetic sample-dataset generation (classification/regression) for demos, docs, and
tests when a project has no data of its own yet.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.datasets import make_classification, make_regression


def _write_csv(X, y, path) -> Path:
    columns = [f"f{i}" for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=columns)
    df["target"] = y
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def make_sample_classification(path, n_samples: int = 200, n_features: int = 5, random_state: int = 42) -> Path:
    """Generate a synthetic binary classification dataset and write it to `path` as CSV
    with columns `f0..fN` + `target`. Returns the written Path."""
    n_informative = min(n_features, max(2, n_features - 2))
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        n_redundant=0,
        n_clusters_per_class=1,
        random_state=random_state,
    )
    return _write_csv(X, y, path)


def make_sample_regression(path, n_samples: int = 200, n_features: int = 5, random_state: int = 42) -> Path:
    """Generate a synthetic regression dataset (continuous target) and write it to `path`
    as CSV with columns `f0..fN` + `target`. Returns the written Path."""
    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_features,
        noise=10.0,
        random_state=random_state,
    )
    return _write_csv(X, y, path)
