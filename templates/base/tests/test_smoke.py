"""Smoke test — the package imports cleanly and SEED is configured."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import {{pkg}}  # noqa: E402


def test_package_imports():
    assert {{pkg}} is not None


def test_seed_is_set():
    assert isinstance({{pkg}}.SEED, int)
    assert {{pkg}}.SEED == 42


def test_config_has_paths():
    assert "data_raw" in {{pkg}}.PATHS
