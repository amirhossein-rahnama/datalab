#!/usr/bin/env python3
"""datalab setup - install Python dependencies with near-zero manual setup.

Core dependencies (scaffolding, EDA, modeling, verification, PDF/PPTX docs) are all a new
user needs, and install by default. Heavier, feature-gated dependencies stay opt-in so the
default install stays fast and light:

    python scripts/setup.py                  # core only (default)
    python scripts/setup.py --full            # + optional (SHAP, Optuna, Evidently, ...)
    python scripts/setup.py --genai           # + GenAI/RAG (LangChain, ChromaDB, ragas, ...)
    python scripts/setup.py --full --genai    # everything
    python scripts/setup.py --dry-run         # print the pip commands without installing

See scripts/requirements.txt, scripts/requirements-optional.txt, and
scripts/requirements-genai.txt for exactly what each group installs.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REQUIREMENTS_CORE = SCRIPTS_DIR / "requirements.txt"
REQUIREMENTS_OPTIONAL = SCRIPTS_DIR / "requirements-optional.txt"
REQUIREMENTS_GENAI = SCRIPTS_DIR / "requirements-genai.txt"

GROUP_LABELS = {
    REQUIREMENTS_CORE: "core",
    REQUIREMENTS_OPTIONAL: "optional (--full)",
    REQUIREMENTS_GENAI: "genai (--genai)",
}


def pip_command(req_file) -> list[str]:
    """Build the argv for `pip install -r <req_file>`. Does not run anything."""
    return [sys.executable, "-m", "pip", "install", "-r", str(req_file)]


def plan(full: bool = False, genai: bool = False) -> list[Path]:
    """Return the ordered list of requirements files to install for the given flags.

    Core is always included. `full` adds the optional (feature-gated) group, `genai` adds
    the GenAI/RAG group. The two flags are independent and can be combined.
    """
    req_files = [REQUIREMENTS_CORE]
    if full:
        req_files.append(REQUIREMENTS_OPTIONAL)
    if genai:
        req_files.append(REQUIREMENTS_GENAI)
    return req_files


def install_group(req_file: Path, *, dry_run: bool = False) -> dict:
    """Install one requirements file.

    Never raises: any failure (missing file, non-zero pip exit, pip not runnable, ...) is
    caught and returned as `{"ok": False, "detail": ...}` so one group failing never stops
    the rest of the run.
    """
    label = GROUP_LABELS.get(req_file, req_file.stem)
    cmd = pip_command(req_file)

    if dry_run:
        return {"label": label, "req_file": req_file, "ok": True, "detail": " ".join(cmd)}

    if not req_file.exists():
        return {"label": label, "req_file": req_file, "ok": False, "detail": f"missing file: {req_file}"}

    print(f"--> Installing {label} dependencies ({req_file.name}) ...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        return {"label": label, "req_file": req_file, "ok": False, "detail": f"pip exited with status {exc.returncode}"}
    except Exception as exc:  # pragma: no cover - defensive: one group's failure must never crash setup
        return {"label": label, "req_file": req_file, "ok": False, "detail": str(exc)}
    return {"label": label, "req_file": req_file, "ok": True, "detail": "installed"}


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Install datalab's Python dependencies")
    ap.add_argument("--full", action="store_true", help="also install scripts/requirements-optional.txt")
    ap.add_argument("--genai", action="store_true", help="also install scripts/requirements-genai.txt")
    ap.add_argument("--dry-run", action="store_true", help="print the pip commands without installing anything")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    req_files = plan(full=args.full, genai=args.genai)

    print("datalab setup")
    print("=" * 40)

    if args.dry_run:
        print("Dry run -- nothing will be installed.\n")
        results = [install_group(req_file, dry_run=True) for req_file in req_files]
        for r in results:
            print(f"[DRY] {r['label']}: {r['detail']}")
        print("\nRe-run without --dry-run to actually install.")
        return 0

    results = [install_group(req_file, dry_run=False) for req_file in req_files]

    print()
    for r in results:
        status = "OK  " if r["ok"] else "FAIL"
        suffix = "" if r["ok"] else f" -- {r['detail']}"
        print(f"[{status}] {r['label']} ({r['req_file'].name}){suffix}")

    failed = [r for r in results if not r["ok"]]
    if failed:
        core_failed = any(r["req_file"] == REQUIREMENTS_CORE for r in failed)
        print("\nSome dependency group(s) failed to install. Retry by hand with:")
        for r in failed:
            print("  " + " ".join(pip_command(r["req_file"])))
        if core_failed:
            print("\nCore dependencies failed -- datalab's scripts may not work until this is fixed.")
        else:
            print("\nCore dependencies are installed, so datalab's core features work.")
            print("The optional/genai group(s) above are only needed for those specific features.")
        return 1

    print("\nAll set -- core dependencies are installed.")
    tips = []
    if not args.full:
        tips.append(
            "  python scripts/setup.py --full    "
            "# SHAP, pandera, Optuna, Evidently, pip-audit, DVC/MLflow/FastAPI/uvicorn"
        )
    if not args.genai:
        tips.append("  python scripts/setup.py --genai   # LangChain, ChromaDB, sentence-transformers, ragas")
    if tips:
        print("\nOptional feature installs (only if/when you need them):")
        for tip in tips:
            print(tip)
    print("\nNext: run `python scripts/doctor.py` to verify your environment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
