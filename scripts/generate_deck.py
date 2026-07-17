#!/usr/bin/env python3
"""Markdown outline -> PPTX via python-pptx.

Outline format: lines starting with '# ' begin a new slide; '- '/'* ' lines (or
plain non-empty lines) become bullets on the current slide.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt


def _parse(outline_text: str):
    slides = []
    current = None
    for raw in outline_text.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            if current:
                slides.append(current)
            current = {"title": line[2:].strip(), "bullets": []}
        elif line.strip().startswith(("- ", "* ")):
            if current is None:
                current = {"title": "", "bullets": []}
            current["bullets"].append(line.strip()[2:])
        elif line.strip():
            if current is None:
                current = {"title": line.strip(), "bullets": []}
            else:
                current["bullets"].append(line.strip())
    if current:
        slides.append(current)
    return slides


def outline_to_pptx(outline_text: str, output_path, title: str | None = None) -> Path:
    output_path = Path(output_path)
    prs = Presentation()
    if title:
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = title
    for spec in _parse(outline_text):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = spec["title"]
        body = slide.placeholders[1].text_frame
        body.clear()
        for j, bullet in enumerate(spec["bullets"]):
            para = body.paragraphs[0] if j == 0 else body.add_paragraph()
            para.text = bullet
            para.font.size = Pt(18)
    prs.save(str(output_path))
    return output_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Markdown outline -> PPTX")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--title", default=None)
    args = ap.parse_args(argv)
    text = Path(args.input).read_text(encoding="utf-8")
    out = outline_to_pptx(text, args.output, args.title)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
