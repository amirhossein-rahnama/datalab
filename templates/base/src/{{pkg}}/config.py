"""Configuration loader for {{project}}.

Reads config.yaml from the project root and exposes SEED plus resolved paths.
Import SEED (and use it everywhere randomness happens) to keep every run
reproducible.
"""
from __future__ import annotations

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG: dict = load_config()
SEED: int = CONFIG.get("seed", 42)

_raw_paths = CONFIG.get("paths", {})
PATHS: dict[str, Path] = {name: (PROJECT_ROOT / value) for name, value in _raw_paths.items()}
