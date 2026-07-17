"""Data-drift monitoring for {{project}}, via Evidently.

Evidently is imported lazily so this module doesn't hard-fail for users who
haven't installed the +mlops tier's dependencies yet.

Usage:
    python monitoring/drift.py --reference data/processed/train.csv --current data/processed/latest.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path


def _evidently():
    try:
        from evidently.metric_preset import DataDriftPreset
        from evidently.report import Report
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "evidently is required for drift monitoring. Install it with: pip install evidently"
        ) from exc
    return Report, DataDriftPreset


def run_drift_report(reference_path: Path, current_path: Path, output_html: Path) -> Path:
    import pandas as pd

    Report, DataDriftPreset = _evidently()

    reference = pd.read_csv(reference_path)
    current = pd.read_csv(current_path)

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)

    output_html = Path(output_html)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    report.save_html(str(output_html))
    return output_html


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run an Evidently data-drift report for {{project}}")
    ap.add_argument("--reference", required=True, help="Path to the reference (training) dataset CSV")
    ap.add_argument("--current", required=True, help="Path to the current (production) dataset CSV")
    ap.add_argument("--output", default="reports/drift_report.html")
    args = ap.parse_args(argv)

    out = run_drift_report(Path(args.reference), Path(args.current), Path(args.output))
    print(f"[drift] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
