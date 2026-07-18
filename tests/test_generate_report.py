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


TABLE_MD = "# Results\n\n| Model | Acc |\n|-------|-----|\n| A | 0.9 |\n| B | 0.8 |\n"


def test_parse_table_skips_separator_row():
    rows = generate_report._parse_table(["| Model | Acc |", "|---|---|", "| A | 0.9 |"])
    assert rows == [["Model", "Acc"], ["A", "0.9"]]


def test_table_renders_as_table_flowable():
    from reportlab.platypus import Table
    story = generate_report.markdown_to_story(TABLE_MD, generate_report._styles())
    assert any(isinstance(f, Table) for f in story)


def test_table_pdf_is_valid(tmp_path):
    out = tmp_path / "t.pdf"
    generate_report.markdown_to_pdf(TABLE_MD, out)
    assert out.read_bytes()[:5] == b"%PDF-"


def test_image_embeds_when_present(tmp_path):
    from reportlab.platypus import Image
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    img = tmp_path / "fig.png"
    fig = plt.figure()
    plt.plot([0, 1], [1, 0])
    fig.savefig(img)
    plt.close(fig)
    story = generate_report.markdown_to_story("![f](fig.png)\n", generate_report._styles(), base_dir=tmp_path)
    assert any(isinstance(f, Image) for f in story)


def test_missing_image_is_skipped_gracefully(tmp_path):
    from reportlab.platypus import Image
    story = generate_report.markdown_to_story("![f](nope.png)\n", generate_report._styles(), base_dir=tmp_path)
    assert not any(isinstance(f, Image) for f in story)
