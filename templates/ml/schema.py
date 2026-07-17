"""Data schema contract for {{project}}, enforced with pandera.

`pandera` is imported lazily so this module — and anything that imports it —
doesn't hard-fail for users who haven't installed the +ml tier's dependencies
yet. Run this file directly to validate a CSV against the schema.
"""
from __future__ import annotations

import argparse


def _pandera():
    try:
        import pandera as pa
        from pandera import Column, DataFrameSchema
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "pandera is required for schema validation. Install it with: pip install pandera"
        ) from exc
    return pa, Column, DataFrameSchema


def build_schema():
    """Define the expected shape of the raw/processed dataset. Edit for your data."""
    pa, Column, DataFrameSchema = _pandera()
    return DataFrameSchema(
        columns={
            # "feature_1": Column(float, nullable=True),
            # "target": Column(int, nullable=False),
        },
        strict=False,
        coerce=True,
    )


def validate(df) -> None:
    """Raise pandera.errors.SchemaErrors if `df` doesn't match the contract."""
    schema = build_schema()
    schema.validate(df, lazy=True)


def main(argv=None) -> int:
    import pandas as pd

    ap = argparse.ArgumentParser(description="Validate a CSV against the {{project}} schema")
    ap.add_argument("--input", required=True)
    args = ap.parse_args(argv)

    df = pd.read_csv(args.input)
    validate(df)
    print(f"[schema] {args.input} is valid ({len(df)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
