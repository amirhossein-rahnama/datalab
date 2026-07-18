#!/usr/bin/env python3
"""datalab scaffold renderer - non-clobbering template -> project tree renderer.

Walks a template directory (e.g. templates/base), substitutes `{{key}}` tokens
(from `context`, e.g. {{pkg}}, {{project}}, {{python}}) in both file CONTENTS and
PATH COMPONENTS, and writes the result into a destination project directory.
Existing destination files are never overwritten unless `overwrite=True`.

Also loads templates/stacks.yaml, the declarative task-type -> package set +
recipe mapping that is the single source of truth for what the `scaffold` skill
installs per task type / tier.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

TOKEN_RE = re.compile(r"\{\{(\w+)\}\}")


def load_stacks(path: str = "templates/stacks.yaml") -> dict:
    """Load and parse `templates/stacks.yaml` into a plain dict."""
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _substitute(text: str, context: dict) -> str:
    """Replace every `{{key}}` occurrence in `text` with `str(context[key])`.

    Tokens whose key is missing from `context` are left untouched (rather than
    raising) so a template can be rendered with a partial context.
    """

    def _repl(match: re.Match) -> str:
        key = match.group(1)
        return str(context[key]) if key in context else match.group(0)

    return TOKEN_RE.sub(_repl, text)


def _render_path(relative_parts, context: dict) -> Path:
    """Substitute `{{key}}` tokens in each path component, e.g. a `{{pkg}}` dir."""
    return Path(*(_substitute(part, context) for part in relative_parts))


def render(template_dir, dest_dir, context: dict, overwrite: bool = False) -> dict:
    """Render every file under `template_dir` into `dest_dir`.

    `{{key}}` tokens from `context` are substituted in both file contents and
    path components (so a directory/file literally named `{{pkg}}` is renamed
    to the package name). Files are treated as UTF-8 text; if a file fails to
    decode as UTF-8 it is copied byte-for-byte instead (binary-safe fallback) -
    path substitution still applies to binary files.

    Non-clobbering by default: if a destination file already exists and
    `overwrite` is False, it is left completely untouched and its relative
    path is recorded in `skipped` instead of `written`.

    Returns {"written": [relative posix paths], "skipped": [relative posix paths]}.
    """
    template_dir = Path(template_dir)
    dest_dir = Path(dest_dir)

    if not template_dir.is_dir():
        raise FileNotFoundError(f"template directory not found: {template_dir}")

    written: list[str] = []
    skipped: list[str] = []

    source_files = sorted(
        (p for p in template_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(template_dir).as_posix(),
    )

    for src_path in source_files:
        relative_parts = src_path.relative_to(template_dir).parts
        rel_dest = _render_path(relative_parts, context)
        rel_str = rel_dest.as_posix()
        dest_path = dest_dir / rel_dest

        if dest_path.exists() and not overwrite:
            skipped.append(rel_str)
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        raw_bytes = src_path.read_bytes()
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            dest_path.write_bytes(raw_bytes)
        else:
            dest_path.write_text(_substitute(text, context), encoding="utf-8")

        written.append(rel_str)

    return {"written": written, "skipped": skipped}


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Render a datalab template tree into a destination project directory."
    )
    parser.add_argument("--template", required=True, help="Template directory, e.g. templates/base")
    parser.add_argument("--dest", required=True, help="Destination project directory")
    parser.add_argument("--pkg", required=True, help="Importable Python package name, e.g. my_project")
    parser.add_argument("--project", required=True, help="Human-readable project name")
    parser.add_argument("--python", default="3.11", help="Target Python version (default: 3.11)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing destination files instead of skipping them",
    )
    args = parser.parse_args(argv)

    context = {"pkg": args.pkg, "project": args.project, "python": args.python}
    result = render(args.template, args.dest, context, overwrite=args.overwrite)

    print(f"[scaffold] {args.template} -> {args.dest}")
    print(f"  written: {len(result['written'])}")
    for path in result["written"]:
        print(f"    + {path}")
    if result["skipped"]:
        print(f"  skipped (already exist): {len(result['skipped'])}")
        for path in result["skipped"]:
            print(f"    - {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
