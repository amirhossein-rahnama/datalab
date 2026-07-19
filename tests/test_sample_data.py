import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pandas as pd  # noqa: E402
import sample_data  # noqa: E402

def test_make_sample_classification_writes_csv_with_target(tmp_path):
    out = tmp_path / "clf.csv"
    result = sample_data.make_sample_classification(out, n_samples=50, n_features=4, random_state=0)
    assert result == out
    df = pd.read_csv(out)
    assert len(df) == 50
    assert list(df.columns) == ["f0", "f1", "f2", "f3", "target"]

def test_make_sample_classification_default_row_count(tmp_path):
    out = tmp_path / "clf_default.csv"
    sample_data.make_sample_classification(out)
    df = pd.read_csv(out)
    assert len(df) == 200
    assert df["target"].nunique() <= 10

def test_make_sample_regression_writes_csv_with_continuous_target(tmp_path):
    out = tmp_path / "reg.csv"
    result = sample_data.make_sample_regression(out, n_samples=30, n_features=3, random_state=0)
    assert result == out
    df = pd.read_csv(out)
    assert len(df) == 30
    assert list(df.columns) == ["f0", "f1", "f2", "target"]
    assert df["target"].nunique() > 10

def test_cli_writes_classification_csv(tmp_path):
    out = tmp_path / "cli.csv"
    rc = sample_data.main(
        ["--task-type", "classification", "--output", str(out),
         "--n-samples", "40", "--n-features", "3", "--seed", "1"]
    )
    assert rc == 0
    df = pd.read_csv(out)
    assert len(df) == 40 and "target" in df.columns
