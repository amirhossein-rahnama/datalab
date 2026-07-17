#!/usr/bin/env python3
"""Jupyter notebook (.ipynb) -> Markdown."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def notebook_to_markdown(nb: dict, include_outputs: bool = True) -> str:
    parts: list[str] = []
    for cell in nb.get("cells", []):
        source = "".join(cell.get("source", []))
        ctype = cell.get("cell_type")
        if ctype == "markdown":
            parts.append(source)
        elif ctype == "code":
            parts.append(f"```python\n{source}\n```")
            if include_outputs:
                for out in cell.get("outputs", []):
                    text = out.get("text")
                    if text is None:
                        text = out.get("data", {}).get("text/plain")
                    if isinstance(text, list):
                        text = "".join(text)
                    if text:
                        parts.append(f"```\n{text}\n```")
    return "\n\n".join(parts) + "\n"


def convert_file(path, output=None, include_outputs: bool = True) -> Path:
    path = Path(path)
    nb = json.loads(path.read_text(encoding="utf-8"))
    md = notebook_to_markdown(nb, include_outputs)
    output = Path(output) if output else path.with_suffix(".md")
    output.write_text(md, encoding="utf-8")
    return output


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Notebook -> Markdown")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=None)
    ap.add_argument("--no-outputs", action="store_true")
    args = ap.parse_args(argv)
    out = convert_file(args.input, args.output, not args.no_outputs)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
