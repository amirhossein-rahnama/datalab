import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generate_report  # noqa: E402

SAMPLE = "# Title\n\nA paragraph with **bold** and *italic* and `code`.\n\n## Section\n\n- one\n- two\n"

def test_produces_nonempty_pdf(tmp_path):
    out = tmp_path / "report.pdf"
    result = generate_report.markdown_to_pdf(SAMPLE, out, title="My Report")
    assert result == out
    assert out.exists() and out.stat().st_size > 0

def test_output_is_a_pdf(tmp_path):
    out = tmp_path / "report.pdf"
    generate_report.markdown_to_pdf(SAMPLE, out)
    assert out.read_bytes()[:5] == b"%PDF-"

def test_inline_formatting_converts_markup():
    assert generate_report._inline("**b**") == "<b>b</b>"
    assert generate_report._inline("*i*") == "<i>i</i>"
