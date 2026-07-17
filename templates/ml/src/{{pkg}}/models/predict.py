"""Inference for {{project}} — loads a fitted pipeline and predicts on new data.

Keep this in sync with train.py: the same Pipeline (preprocessing + model)
that was fit in training must be the one used here, so no transform step can
leak, drift, or diverge between train and serve time.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import joblib
import pandas as pd

MODEL_PATH_DEFAULT = Path(__file__).resolve().parents[3] / "models" / "pipeline.joblib"


def load_pipeline(path: Path = MODEL_PATH_DEFAULT):
    return joblib.load(path)


def predict(df: pd.DataFrame, pipeline=None, model_path: Path = MODEL_PATH_DEFAULT) -> pd.Series:
    if pipeline is None:
        pipeline = load_pipeline(model_path)
    preds = pipeline.predict(df)
    return pd.Series(preds, index=df.index, name="prediction")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Predict with the trained {{project}} pipeline")
    ap.add_argument("--input", required=True, help="CSV file with feature columns")
    ap.add_argument("--output", required=True, help="CSV file to write predictions to")
    ap.add_argument("--model", default=str(MODEL_PATH_DEFAULT))
    args = ap.parse_args(argv)

    df = pd.read_csv(args.input)
    preds = predict(df, model_path=Path(args.model))
    preds.to_csv(args.output, index=False)
    print(f"[predict] wrote {len(preds)} predictions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
