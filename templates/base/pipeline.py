#!/usr/bin/env python3
"""{{project}} — end-to-end pipeline skeleton.

Run the whole thing:  python pipeline.py
Run one step only:    python pipeline.py --step train

This is a STARTING POINT — each step below is a minimal working stub that
loads config and prints what it would do. Replace the body of each function
with real logic as the project grows. Steps always read from `config.yaml`
and use the fixed SEED so every run is reproducible.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from {{pkg}}.config import CONFIG, PATHS, SEED  # noqa: E402

STEPS = ["load", "validate", "features", "train", "evaluate", "report"]


# ---- step: load ----
def load():
    """Load raw data. Replace with e.g. pd.read_csv(PATHS['data_raw'] / 'train.csv')."""
    print(f"[load] seed={SEED}  data_raw={PATHS['data_raw']}")
    print("[load] TODO: load your dataset here")
    return None


# ---- step: validate ----
def validate(data=None):
    """Validate schema/quality. Wire up templates/ml/schema.py (pandera) once the +ml tier is added."""
    print("[validate] TODO: validate schema, nulls, dtypes")
    return data


# ---- step: features ----
def features(data=None):
    """Feature engineering. Keep all fitting inside a sklearn Pipeline to avoid leakage."""
    print("[features] TODO: build features")
    return data


# ---- step: train ----
def train(data=None):
    """Train the model(s). Use SEED for every stochastic component (splits, model init)."""
    print(f"[train] TODO: fit model(s) with random_state={SEED}")
    return None


# ---- step: evaluate ----
def evaluate(model=None, data=None):
    """Evaluate against a baseline; write metrics under CONFIG['paths']['reports']."""
    print(f"[evaluate] TODO: score against a Dummy/naive baseline, write to {PATHS['reports']}")
    return {}


# ---- step: report ----
def report(metrics=None):
    """Summarize results. `tasks.py report` calls this step directly."""
    print(f"[report] TODO: write figures to {PATHS['figures']} and a results summary")
    return None


def run_all() -> None:
    data = load()
    data = validate(data)
    data = features(data)
    model = train(data)
    metrics = evaluate(model, data)
    report(metrics)
    print("[pipeline] done")


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="{{project}} pipeline runner")
    parser.add_argument(
        "--step", choices=STEPS, default=None, help="run a single step instead of the full pipeline"
    )
    args = parser.parse_args(argv)

    if args.step is None:
        run_all()
    elif args.step == "load":
        load()
    elif args.step == "validate":
        validate()
    elif args.step == "features":
        features()
    elif args.step == "train":
        train()
    elif args.step == "evaluate":
        evaluate()
    elif args.step == "report":
        report()

    _ = CONFIG  # CONFIG is available for any step that needs the full config dict
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
