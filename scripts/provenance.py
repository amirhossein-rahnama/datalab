#!/usr/bin/env python3
"""Reproducibility provenance manifest: interpreter/platform info, tracked package
versions, git commit, and (optionally) a data-file hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from pathlib import Path

TRACKED_PACKAGES = ["pandas", "numpy", "scikit-learn"]


def _package_versions(packages=TRACKED_PACKAGES) -> dict:
    """Best-effort package version lookup; missing packages map to None."""
    versions = {}
    for pkg in packages:
        try:
            versions[pkg] = importlib_metadata.version(pkg)
        except importlib_metadata.PackageNotFoundError:
            versions[pkg] = None
    return versions


def _git_commit(cwd=None) -> str | None:
    """Current git commit SHA, or None if git is unavailable / cwd isn't a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _sha256_file(path, chunk_size: int = 1 << 20) -> str:
    """Stream a file through SHA-256 in chunks (safe for large data files)."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(seed=None, data_path=None, extra=None) -> dict:
    """Build a reproducibility manifest: timestamp, interpreter, platform, tracked package
    versions, git commit, seed, and (if `data_path` is given) a SHA-256 hash of that file.
    """
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": _package_versions(),
        "git_commit": _git_commit(),
        "seed": seed,
        "data_path": None,
        "data_sha256": None,
    }
    if data_path is not None:
        path = Path(data_path)
        manifest["data_path"] = str(path)
        manifest["data_sha256"] = _sha256_file(path) if path.exists() else None
    if extra:
        manifest["extra"] = extra
    return manifest


def write_manifest(path, **kwargs) -> Path:
    """Build a manifest (see `build_manifest` for kwargs) and write it as JSON to `path`."""
    manifest = build_manifest(**kwargs)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write a reproducibility provenance manifest")
    ap.add_argument("--output", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--data-path", default=None)
    args = ap.parse_args(argv)
    out = write_manifest(args.output, seed=args.seed, data_path=args.data_path)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
