import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pandas as pd  # noqa: E402
import profile_data  # noqa: E402

CSV_TEXT = (
    "a,b,label\n"
    "1,2.5,yes\n"
    "2,3.5,no\n"
    "3,,yes\n"
    "4,4.5,no\n"
)

def _write_csv(tmp_path):
    csv_path = tmp_path / "tiny.csv"
    csv_path.write_text(CSV_TEXT, encoding="utf-8")
    return csv_path

def test_profile_returns_expected_keys(tmp_path):
    result = profile_data.profile(str(_write_csv(tmp_path)))
    for key in ("shape", "columns", "missing_pct", "numeric_summary", "cardinality", "target_guess"):
        assert key in result
    assert result["shape"] == (4, 3)

def test_profile_target_guess_classification_on_strings(tmp_path):
    result = profile_data.profile(str(_write_csv(tmp_path)))
    guess = result["target_guess"]
    assert guess["column"] == "label"
    assert guess["task_type"] == "classification"

def test_profile_missing_pct_detected(tmp_path):
    result = profile_data.profile(str(_write_csv(tmp_path)))
    assert result["missing_pct"]["b"] > 0

def test_profile_target_guess_regression_on_wide_numeric():
    df = pd.DataFrame({"x": range(11), "y": range(11)})
    result = profile_data.profile(df)
    assert result["target_guess"]["column"] == "y"
    assert result["target_guess"]["task_type"] == "regression"

def test_data_dictionary_entries(tmp_path):
    df = pd.read_csv(_write_csv(tmp_path))
    entries = profile_data.data_dictionary(df)
    assert len(entries) == 3
    assert {e["name"] for e in entries} == {"a", "b", "label"}
    for e in entries:
        assert set(e) == {"name", "dtype", "non_null", "missing_pct", "unique", "example"}
