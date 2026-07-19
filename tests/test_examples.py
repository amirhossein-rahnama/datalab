"""Run each worked example end-to-end, so the examples stay real fixtures, not stale demos."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / script)],
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_iris_classification_runs():
    r = _run("examples/iris-classification/src/iris_clf/train.py")
    assert r.returncode == 0, r.stderr[-800:]
    assert "ccuracy" in r.stdout


def test_diabetes_regression_runs():
    r = _run("examples/diabetes-regression/src/diabetes_reg/train.py")
    assert r.returncode == 0, r.stderr[-800:]
    assert "R2" in r.stdout


def test_sales_forecasting_runs():
    r = _run("examples/sales-forecasting/src/sales_ts/forecast.py")
    assert r.returncode == 0, r.stderr[-800:]
    assert "MAE" in r.stdout


def test_rag_retrieval_runs_and_finds_export_doc():
    r = _run("examples/rag-knowledge-base/src/rag_demo/run.py")
    assert r.returncode == 0, r.stderr[-800:]
    # the export query must retrieve the export doc as the top source
    assert "data-export.md" in r.stdout
