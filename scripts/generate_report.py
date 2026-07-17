#!/usr/bin/env python3
"""Markdown -> PDF via reportlab Platypus. Pure Python, no system dependencies."""
from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def _inline(text: str) -> str:
    """Convert a subset of inline Markdown to reportlab markup."""
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    return text


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("DLBody", parent=ss["BodyText"], spaceAfter=6, leading=14))
    return ss


def markdown_to_story(md_text: str, styles):
    story = []
    bullets: list[str] = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(_inline(b), styles["DLBody"])) for b in bullets],
                    bulletType="bullet",
                )
            )
            story.append(Spacer(1, 6))
            bullets = []

    for raw in md_text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_bullets()
        elif line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(_inline(line[4:]), styles["Heading3"]))
        elif line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(_inline(line[3:]), styles["Heading2"]))
        elif line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(_inline(line[2:]), styles["Heading1"]))
        elif line.lstrip().startswith(("- ", "* ")):
            bullets.append(line.lstrip()[2:])
        else:
            flush_bullets()
            story.append(Paragraph(_inline(line), styles["DLBody"]))
    flush_bullets()
    return story


def markdown_to_pdf(md_text: str, output_path, title: str | None = None) -> Path:
    output_path = Path(output_path)
    styles = _styles()
    story = []
    if title:
        story.append(Paragraph(_inline(title), styles["Title"]))
        story.append(Spacer(1, 12))
    story.extend(markdown_to_story(md_text, styles))
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=title or output_path.stem,
    )
    doc.build(story)
    return output_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Markdown -> PDF")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--title", default=None)
    args = ap.parse_args(argv)
    md = Path(args.input).read_text(encoding="utf-8")
    out = markdown_to_pdf(md, args.output, args.title)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
