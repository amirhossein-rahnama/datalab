import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pandas as pd  # noqa: E402
import bigdata  # noqa: E402

N_POS = 120
N_NEG = 80
TOTAL_ROWS = N_POS + N_NEG

def _write_csv(tmp_path):
    lines = ["a,b,target"]
    for i in range(N_POS):
        lines.append(f"{i},{i * 1.5},1")
    for i in range(N_NEG):
        lines.append(f"{N_POS + i},{(N_POS + i) * 1.5},0")
    csv_path = tmp_path / "big.csv"
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path

def test_count_rows_matches_data_row_count(tmp_path):
    csv_path = _write_csv(tmp_path)
    assert bigdata.count_rows(csv_path) == TOTAL_ROWS

def test_count_rows_header_only(tmp_path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("a,b,target\n", encoding="utf-8")
    assert bigdata.count_rows(csv_path) == 0

def test_count_rows_no_trailing_newline(tmp_path):
    csv_path = tmp_path / "no_trailing_nl.csv"
    csv_path.write_text("a,b,target\n1,2,0\n3,4,1", encoding="utf-8")
    assert bigdata.count_rows(csv_path) == 2

def test_sample_csv_stratified_preserves_both_classes(tmp_path):
    csv_path = _write_csv(tmp_path)
    sample = bigdata.sample_csv(csv_path, 50, stratify_col="target", seed=42)
    assert isinstance(sample, pd.DataFrame)
    assert 45 <= len(sample) <= 55

    classes = set(sample["target"].tolist())
    assert classes == {0, 1}

    pos_count = int((sample["target"] == 1).sum())
    pos_fraction = pos_count / len(sample)
    assert abs(pos_fraction - (N_POS / TOTAL_ROWS)) < 0.1  # proportions roughly preserved

def test_sample_csv_without_stratify_returns_requested_size(tmp_path):
    csv_path = _write_csv(tmp_path)
    sample = bigdata.sample_csv(csv_path, 30, seed=0)
    assert isinstance(sample, pd.DataFrame)
    assert len(sample) == 30
    assert list(sample.columns) == ["a", "b", "target"]

def test_sample_csv_n_larger_than_file_returns_all_rows(tmp_path):
    csv_path = _write_csv(tmp_path)
    sample = bigdata.sample_csv(csv_path, TOTAL_ROWS + 1000, seed=0)
    assert len(sample) == TOTAL_ROWS

def test_read_chunked_yields_chunks_summing_to_all_rows(tmp_path):
    csv_path = _write_csv(tmp_path)
    chunks = list(bigdata.read_chunked(csv_path, chunksize=40))
    assert all(isinstance(chunk, pd.DataFrame) for chunk in chunks)
    assert len(chunks) > 1
    assert sum(len(chunk) for chunk in chunks) == TOTAL_ROWS

def test_read_fast_missing_polars_raises_clear_import_error(tmp_path):
    csv_path = _write_csv(tmp_path)
    try:
        import polars  # noqa: F401
    except ImportError:
        pass
    else:
        return  # polars is installed in this environment; nothing to assert here
    try:
        bigdata.read_fast(csv_path)
        assert False, "expected ImportError when polars is missing"
    except ImportError as exc:
        assert "polars" in str(exc)
        assert "pip install" in str(exc)
