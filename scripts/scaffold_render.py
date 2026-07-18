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


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def slugify_pkg(project: str) -> str:
    """Derive an importable package name from a human-readable project name."""
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", project.strip().lower()).strip("_")
    if not slug:
        return "project"
    if slug[0].isdigit():
        slug = "p_" + slug
    return slug


def augment_requirements(dest_dir, task_type=None, tiers=(), stacks_path=None) -> list:
    """Append task-type/tier packages from stacks.yaml to dest requirements.txt.

    Deduplicates against packages already listed. No-op (returns []) if
    requirements.txt is absent or stacks.yaml can't be read.
    """
    req = Path(dest_dir) / "requirements.txt"
    if not req.exists():
        return []
    try:
        stacks = load_stacks(str(stacks_path or (PLUGIN_ROOT / "templates" / "stacks.yaml")))
    except Exception:
        return []
    wanted = list((stacks.get("tasks", {}).get(task_type) or {}).get("packages") or []) if task_type else []
    for tier in tiers:
        wanted += list((stacks.get("tiers", {}).get(tier) or {}).get("packages") or [])
    existing_text = req.read_text(encoding="utf-8")
    have = {
        re.split(r"[<>=!~ ]", ln.strip())[0].lower()
        for ln in existing_text.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    }
    added = []
    for pkg in wanted:
        name = re.split(r"[<>=!~ ]", pkg)[0].lower()
        if name and name not in have:
            added.append(pkg)
            have.add(name)
    if added:
        req.write_text(
            existing_text.rstrip("\n") + "\n# task/tier packages\n" + "\n".join(added) + "\n",
            encoding="utf-8",
        )
    return added


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Render a datalab template tree into a destination project directory."
    )
    parser.add_argument("--template", help="Single template directory, e.g. templates/base (low-level mode)")
    parser.add_argument("--tier", help="Comma-separated tiers rendered in order, e.g. base,ml (high-level mode)")
    parser.add_argument("--dest", required=True, help="Destination project directory")
    parser.add_argument("--pkg", help="Importable package name (default: derived from --project)")
    parser.add_argument("--project", required=True, help="Human-readable project name")
    parser.add_argument("--python", default="3.11", help="Target Python version (default: 3.11)")
    parser.add_argument("--task-type", dest="task_type", help="Task type; adds packages from stacks.yaml")
    parser.add_argument("--manager", default="uv", help="Package manager label (default: uv)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing destination files instead of skipping them",
    )
    args = parser.parse_args(argv)

    if not args.template and not args.tier:
        parser.error("one of --template or --tier is required")

    pkg = args.pkg or slugify_pkg(args.project)
    context = {"pkg": pkg, "project": args.project, "python": args.python}

    # Low-level mode: render a single template dir (output format unchanged).
    if args.template:
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

    # High-level mode: render one or more tiers in order from the bundled templates.
    tiers = [t.strip() for t in args.tier.split(",") if t.strip()]
    written_total, skipped_total = [], []
    for tier in tiers:
        tdir = PLUGIN_ROOT / "templates" / tier
        if not tdir.is_dir():
            print(f"[scaffold] WARNING: unknown tier '{tier}' ({tdir} not found) - skipped")
            continue
        result = render(tdir, args.dest, context, overwrite=args.overwrite)
        written_total += [f"{tier}/{p}" for p in result["written"]]
        skipped_total += [f"{tier}/{p}" for p in result["skipped"]]
    added = augment_requirements(args.dest, task_type=args.task_type, tiers=tiers)

    print(f"[scaffold] tiers={','.join(tiers)} -> {args.dest} (pkg={pkg}, python={args.python}, manager={args.manager})")
    print(f"  written: {len(written_total)}")
    for path in written_total:
        print(f"    + {path}")
    if skipped_total:
        print(f"  skipped (already exist): {len(skipped_total)}")
        for path in skipped_total:
            print(f"    - {path}")
    if added:
        print(f"  requirements.txt: +{len(added)} task/tier package(s): {', '.join(added)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
