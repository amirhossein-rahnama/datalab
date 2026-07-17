import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generate_deck  # noqa: E402

OUTLINE = "# Problem\n- context\n- goal\n\n# Results\n- accuracy 0.92\n- beats baseline\n"

def test_parse_splits_slides():
    slides = generate_deck._parse(OUTLINE)
    assert [s["title"] for s in slides] == ["Problem", "Results"]
    assert slides[0]["bullets"] == ["context", "goal"]

def test_produces_valid_pptx(tmp_path):
    from pptx import Presentation
    out = tmp_path / "deck.pptx"
    result = generate_deck.outline_to_pptx(OUTLINE, out, title="My Deck")
    assert result == out and out.exists() and out.stat().st_size > 0
    prs = Presentation(str(out))
    # title slide + 2 content slides
    assert len(prs.slides) == 3
