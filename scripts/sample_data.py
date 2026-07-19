#!/usr/bin/env python3
"""Synthetic sample-dataset generation (classification/regression) for demos, docs, and
tests when a project has no data of its own yet.
"""
from __future__ import annotations

import argparse
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate a synthetic sample dataset (CSV with a 'target' column)"
    )
    ap.add_argument("--task-type", dest="task_type", default="classification",
                    choices=["classification", "regression"])
    ap.add_argument("--output", required=True, help="CSV path to write")
    ap.add_argument("--n-samples", dest="n_samples", type=int, default=200)
    ap.add_argument("--n-features", dest="n_features", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)
    generator = make_sample_regression if args.task_type == "regression" else make_sample_classification
    out = generator(args.output, n_samples=args.n_samples, n_features=args.n_features, random_state=args.seed)
    print(f"[sample_data] wrote {args.task_type} dataset ({args.n_samples} rows) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
