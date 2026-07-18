#!/usr/bin/env python3
"""datalab doctor - environment & plugin health check."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REQUIRED_PACKAGES = ["reportlab", "pptx", "pandas", "numpy", "sklearn", "matplotlib", "yaml", "nbformat", "nbclient"]
PIP_NAMES = {"pptx": "python-pptx", "sklearn": "scikit-learn", "yaml": "pyyaml"}
MIN_PYTHON = (3, 10)

# Heavy, feature-gated dependencies (see scripts/requirements-optional.txt). None of these
# are required for datalab's core scripts - each is only needed for the feature listed.
# Import name may differ from the pip package name (e.g. pip-audit -> pip_audit).
OPTIONAL_PACKAGES = [
    {"module": "shap", "pip": "shap", "feature": "explainability"},
    {"module": "pandera", "pip": "pandera", "feature": "data validation"},
    {"module": "optuna", "pip": "optuna", "feature": "hyperparameter tuning"},
    {"module": "evidently", "pip": "evidently", "feature": "drift monitoring"},
    {"module": "pip_audit", "pip": "pip-audit", "feature": "dependency security scan"},
    {"module": "dvc", "pip": "dvc", "feature": "mlops"},
    {"module": "mlflow", "pip": "mlflow", "feature": "mlops"},
    {"module": "fastapi", "pip": "fastapi", "feature": "mlops"},
    {"module": "uvicorn", "pip": "uvicorn", "feature": "mlops"},
]


def check_python(version=None) -> dict:
    version = version if version is not None else sys.version_info
    ok = tuple(version[:2]) >= MIN_PYTHON
    return {
        "name": "python",
        "ok": ok,
        "detail": f"{version[0]}.{version[1]} (need >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]})",
    }


def check_packages(packages=REQUIRED_PACKAGES) -> list[dict]:
    results = []
    for mod in packages:
        found = importlib.util.find_spec(mod) is not None
        results.append({"name": PIP_NAMES.get(mod, mod), "module": mod, "ok": found})
    return results


def check_optional(packages=OPTIONAL_PACKAGES) -> list[dict]:
    """Presence check for heavy, feature-gated packages. Absence is informational, never a failure."""
    results = []
    for pkg in packages:
        found = importlib.util.find_spec(pkg["module"]) is not None
        results.append({"name": pkg["pip"], "module": pkg["module"], "feature": pkg["feature"], "ok": found})
    return results


def check_plugin(root: Path) -> dict:
    manifest = Path(root) / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        return {"name": "plugin.json", "ok": False, "detail": "missing"}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"name": "plugin.json", "ok": False, "detail": f"invalid JSON: {exc}"}
    return {"name": "plugin.json", "ok": "name" in data, "detail": data.get("name", "no name field")}


def missing_pip_install(package_results) -> str | None:
    missing = [p["name"] for p in package_results if not p["ok"]]
    return "pip install " + " ".join(missing) if missing else None


def run(root: Path) -> dict:
    py = check_python()
    pkgs = check_packages()
    optional = check_optional()
    plugin = check_plugin(root)
    # healthy depends ONLY on python + plugin wiring + CORE packages - optional
    # (feature-gated) packages are informational and never block a healthy status.
    healthy = py["ok"] and plugin["ok"] and all(p["ok"] for p in pkgs)
    return {
        "python": py,
        "packages": pkgs,
        "optional": optional,
        "plugin": plugin,
        "healthy": healthy,
        "fix": missing_pip_install(pkgs),
    }


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    root = Path(argv[0]) if argv else Path(__file__).resolve().parents[1]
    report = run(root)
    print("datalab doctor\n" + "=" * 40)
    print(f"[{'OK ' if report['python']['ok'] else 'FAIL'}] Python {report['python']['detail']}")
    print(f"[{'OK ' if report['plugin']['ok'] else 'FAIL'}] plugin.json: {report['plugin']['detail']}")
    for pkg in report["packages"]:
        print(f"[{'OK ' if pkg['ok'] else 'FAIL'}] {pkg['name']}")
    if report["fix"]:
        print("\nMissing core packages. Fix with:")
        print("  python scripts/setup.py")
        print(f"  (or manually: {report['fix']})")

    print("\nOptional (feature-gated) packages:")
    missing_optional = False
    for pkg in report["optional"]:
        if pkg["ok"]:
            print(f"[OK ] {pkg['name']} (optional: {pkg['feature']})")
        else:
            missing_optional = True
            print(f"[--] {pkg['name']} (optional: {pkg['feature']}) -> pip install {pkg['name']}")
    if missing_optional:
        print("\nInstall optional features with: python scripts/setup.py --full")
        print("(GenAI/RAG deps: python scripts/setup.py --genai)")

    print("\nHealthy!" if report["healthy"] else "\nIssues found - see above.")
    return 0 if report["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
