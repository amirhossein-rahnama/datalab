import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import plots  # noqa: E402


def _nonempty_png(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0 and path.read_bytes()[:4] == b"\x89PNG"


def test_plot_confusion_matrix(tmp_path):
    out = plots.plot_confusion_matrix([0, 1, 1, 0], [0, 1, 0, 0], tmp_path / "cm.png")
    assert _nonempty_png(Path(out))


def test_plot_learning_curve(tmp_path):
    out = plots.plot_learning_curve([10, 20, 30], [0.7, 0.8, 0.85], [0.6, 0.7, 0.72], tmp_path / "lc.png")
    assert _nonempty_png(Path(out))


def test_plot_roc(tmp_path):
    out = plots.plot_roc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8], tmp_path / "roc.png")
    assert _nonempty_png(Path(out))


def test_plot_residuals(tmp_path):
    out = plots.plot_residuals([1.0, 2.0, 3.0], [1.1, 1.9, 3.2], tmp_path / "res.png")
    assert _nonempty_png(Path(out))
