#!/usr/bin/env python3
"""Data profiling: shape, dtypes, missingness, cardinality, and a target/task-type guess.

Accepts either an in-memory pandas DataFrame or a path to a CSV/Parquet file, so it can be
used both programmatically (by other datalab scripts/skills) and from the CLI.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _load(data) -> pd.DataFrame:
    """Return a DataFrame for `data`, which may already be one or a path to CSV/Parquet."""
    if isinstance(data, pd.DataFrame):
        return data
    path = Path(data)
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _jsonable(value):
    """Best-effort conversion of a pandas/numpy scalar to a plain JSON-serializable value."""
    if value is None:
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    return value if isinstance(value, (str, int, float, bool)) else str(value)


def _guess_target(df: pd.DataFrame) -> dict:
    """Heuristic target/task guess: last column is the target.

    `task_type` is "classification" if that column is non-numeric or has <= 10 unique
    values, else "regression".
    """
    if df.shape[1] == 0:
        return {"column": None, "task_type": None}
    column = df.columns[-1]
    series = df[column]
    is_numeric = pd.api.types.is_numeric_dtype(series)
    n_unique = int(series.nunique(dropna=True))
    task_type = "regression" if (is_numeric and n_unique > 10) else "classification"
    return {"column": column, "task_type": task_type}


def profile(data) -> dict:
    """Profile a dataset: shape, dtypes, missingness, numeric summary, cardinality, target guess.

    `data` may be a pandas DataFrame or a path to a CSV/Parquet file.
    """
    df = _load(data)

    columns = {col: str(dtype) for col, dtype in df.dtypes.items()}
    missing_pct = {col: float(df[col].isna().mean() * 100) for col in df.columns}
    cardinality = {col: int(df[col].nunique(dropna=True)) for col in df.columns}

    numeric_df = df.select_dtypes(include="number")
    numeric_summary = json.loads(numeric_df.describe().to_json()) if not numeric_df.empty else {}

    return {
        "shape": tuple(df.shape),
        "columns": columns,
        "missing_pct": missing_pct,
        "numeric_summary": numeric_summary,
        "cardinality": cardinality,
        "target_guess": _guess_target(df),
    }


def data_dictionary(df) -> list[dict]:
    """Per-column dictionary: name, dtype, non_null count, missing_pct, unique count, example."""
    df = _load(df)
    entries = []
    for col in df.columns:
        series = df[col]
        non_null = series.dropna()
        example = _jsonable(non_null.iloc[0]) if len(non_null) else None
        entries.append(
            {
                "name": col,
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "missing_pct": float(series.isna().mean() * 100),
                "unique": int(series.nunique(dropna=True)),
                "example": example,
            }
        )
    return entries


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Profile a CSV/Parquet dataset")
    ap.add_argument("--input", required=True, help="Path to a CSV or Parquet file")
    args = ap.parse_args(argv)
    result = profile(args.input)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
