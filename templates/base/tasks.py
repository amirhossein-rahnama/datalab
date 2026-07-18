#!/usr/bin/env python3
"""Cross-platform task runner for {{project}} - no `make` required.

Usage:
    python tasks.py setup    # pip install -r requirements.txt
    python tasks.py lab      # launch Jupyter Lab
    python tasks.py test     # run pytest
    python tasks.py lint     # run ruff check + format --check
    python tasks.py report   # run the report step of pipeline.py
    python tasks.py run      # run the full pipeline (pipeline.py)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run(cmd: list[str]) -> int:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def setup(_args: argparse.Namespace) -> int:
    return _run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def lab(_args: argparse.Namespace) -> int:
    return _run([sys.executable, "-m", "jupyter", "lab"])


def test(_args: argparse.Namespace) -> int:
    return _run([sys.executable, "-m", "pytest", "-q"])


def lint(_args: argparse.Namespace) -> int:
    code = _run([sys.executable, "-m", "ruff", "check", "."])
    fmt_code = _run([sys.executable, "-m", "ruff", "format", "--check", "."])
    return code or fmt_code


def report(_args: argparse.Namespace) -> int:
    return _run([sys.executable, "pipeline.py", "--step", "report"])


def run(_args: argparse.Namespace) -> int:
    return _run([sys.executable, "pipeline.py"])


COMMANDS = {
    "setup": setup,
    "lab": lab,
    "test": test,
    "lint": lint,
    "report": report,
    "run": run,
}


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Task runner for {{project}} (no make required)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in COMMANDS:
        subparsers.add_parser(name)
    args = parser.parse_args(argv)
    return COMMANDS[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
