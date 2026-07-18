#!/usr/bin/env python3
"""Markdown -> PDF via reportlab Platypus. Pure Python, no system dependencies.

Supports headings, paragraphs, inline bold/italic/code, bullet lists, GitHub-style
tables (`| a | b |`), and embedded images (`![alt](path)`, resolved relative to the
Markdown file's directory).
"""
from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

MAX_CONTENT_WIDTH = 17 * cm  # A4 (21cm) minus 2x2cm margins
IMG_RE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)\s*$")


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
    ss.add(ParagraphStyle("DLTableHeader", parent=ss["BodyText"], textColor=colors.white,
                          fontName="Helvetica-Bold", leading=13))
    ss.add(ParagraphStyle("DLTableCell", parent=ss["BodyText"], leading=13))
    return ss


def _parse_table(lines):
    """Parse GitHub-style table lines into rows of cells; drop the `---` separator row."""
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and all(c and set(c) <= set("-: ") for c in cells):
            continue  # separator row like |---|:--:|
        rows.append(cells)
    return rows


def _make_table(rows, styles):
    ncols = max(len(r) for r in rows)

    def pad(row):
        return row + [""] * (ncols - len(row))

    data = [[Paragraph(_inline(c), styles["DLTableHeader"]) for c in pad(rows[0])]]
    for r in rows[1:]:
        data.append([Paragraph(_inline(c), styles["DLTableCell"]) for c in pad(r)])
    table = Table(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _make_image(src, base_dir):
    """Return a reportlab Image scaled to the page, or None if the file is missing/unreadable."""
    path = Path(src)
    if not path.is_absolute():
        path = Path(base_dir) / src
    if not path.exists():
        return None
    try:
        iw, ih = ImageReader(str(path)).getSize()
    except Exception:
        return None
    width = min(MAX_CONTENT_WIDTH, float(iw))
    height = float(ih) * (width / float(iw))
    return Image(str(path), width=width, height=height)


def markdown_to_story(md_text: str, styles, base_dir=None):
    base_dir = Path(base_dir) if base_dir else Path.cwd()
    story = []
    bullets: list[str] = []
    table_lines: list[str] = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            story.append(ListFlowable(
                [ListItem(Paragraph(_inline(b), styles["DLBody"])) for b in bullets],
                bulletType="bullet"))
            story.append(Spacer(1, 6))
            bullets = []

    def flush_table():
        nonlocal table_lines
        if table_lines:
            rows = _parse_table(table_lines)
            if rows:
                story.append(_make_table(rows, styles))
                story.append(Spacer(1, 8))
            table_lines = []

    def flush():
        flush_bullets()
        flush_table()

    for raw in md_text.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("|") and s.endswith("|"):
            flush_bullets()
            table_lines.append(s)
        elif IMG_RE.match(s):
            flush()
            img = _make_image(IMG_RE.match(s).group(1), base_dir)
            if img is not None:
                story.append(img)
                story.append(Spacer(1, 8))
        elif line.startswith("### "):
            flush()
            story.append(Paragraph(_inline(line[4:]), styles["Heading3"]))
        elif line.startswith("## "):
            flush()
            story.append(Paragraph(_inline(line[3:]), styles["Heading2"]))
        elif line.startswith("# "):
            flush()
            story.append(Paragraph(_inline(line[2:]), styles["Heading1"]))
        elif s.startswith(("- ", "* ")):
            flush_table()
            bullets.append(s[2:])
        else:
            flush()
            story.append(Paragraph(_inline(line), styles["DLBody"]))
    flush()
    return story


def markdown_to_pdf(md_text: str, output_path, title: str | None = None, base_dir=None) -> Path:
    output_path = Path(output_path)
    styles = _styles()
    story = []
    if title:
        story.append(Paragraph(_inline(title), styles["Title"]))
        story.append(Spacer(1, 12))
    story.extend(markdown_to_story(md_text, styles, base_dir=base_dir))
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
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
    md_path = Path(args.input)
    md = md_path.read_text(encoding="utf-8")
    out = markdown_to_pdf(md, args.output, args.title, base_dir=md_path.parent)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
