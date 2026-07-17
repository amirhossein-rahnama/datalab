"""RAG pipeline — step 1: load source documents for {{project}}.

Reads raw documents (.txt/.md) from a directory and returns a list of
plain-text documents with basic metadata, ready for rag/chunk.py. Extend
SUPPORTED_SUFFIXES (and add a parser) for PDF/HTML/etc. as needed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

SUPPORTED_SUFFIXES = {".txt", ".md"}


def load_documents(source_dir: Path) -> list[dict]:
    """Load all supported files under `source_dir` into {source, text} dicts."""
    source_dir = Path(source_dir)
    docs = []
    for path in sorted(source_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore")
            docs.append({"source": str(path), "text": text})
    return docs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Load raw documents for the {{project}} RAG pipeline")
    ap.add_argument("--source", required=True, help="Directory of source documents")
    args = ap.parse_args(argv)

    docs = load_documents(Path(args.source))
    print(f"[loader] loaded {len(docs)} documents from {args.source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
