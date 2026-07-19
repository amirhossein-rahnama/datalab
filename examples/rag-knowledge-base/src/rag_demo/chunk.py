"""Load the corpus and split each document into retrieval-sized chunks.

Chunking strategy: split each markdown file on blank-line-separated paragraphs (a
heading line is folded into the paragraph that immediately follows it, so a short
"# Title" line isn't left as its own near-empty, context-free chunk), then further
split any paragraph longer than MAX_CHUNK_CHARS into fixed-size, word-boundary-aligned
pieces. This keeps most chunks topically coherent (one idea per paragraph) while
bounding chunk length so retrieval scores aren't skewed by a handful of very long
chunks.

Usage:
    from rag_demo.chunk import load_and_chunk
    chunks = load_and_chunk()  # [{"doc": "billing.md", "text": "..."}, ...]
"""
from __future__ import annotations

from pathlib import Path

# examples/rag-knowledge-base/src/rag_demo/chunk.py -> examples/rag-knowledge-base/corpus
DEFAULT_CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus"
MAX_CHUNK_CHARS = 500


def _split_paragraphs(text: str) -> list[str]:
    """Split markdown text into non-empty paragraphs, folding headings into the next paragraph."""
    raw_blocks = [block.strip() for block in text.split("\n\n")]
    raw_blocks = [block for block in raw_blocks if block]

    paragraphs: list[str] = []
    pending_heading = ""
    for block in raw_blocks:
        if block.startswith("#"):
            pending_heading = block.lstrip("#").strip()
            continue
        if pending_heading:
            block = f"{pending_heading}: {block}"
            pending_heading = ""
        paragraphs.append(block)
    return paragraphs


def _split_long_paragraph(paragraph: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Break a paragraph longer than max_chars into pieces on word boundaries."""
    if len(paragraph) <= max_chars:
        return [paragraph]

    words = paragraph.split(" ")
    pieces: list[str] = []
    current: list[str] = []
    current_len = 0
    for word in words:
        # +1 accounts for the space that will join `current` back together
        if current and current_len + len(word) + 1 > max_chars:
            pieces.append(" ".join(current))
            current, current_len = [], 0
        current.append(word)
        current_len += len(word) + 1
    if current:
        pieces.append(" ".join(current))
    return pieces


def load_corpus(corpus_dir: Path = DEFAULT_CORPUS_DIR) -> list[dict]:
    """Load every `.md` file in corpus_dir.

    Returns [{"doc": "billing.md", "text": "<full file contents>"}, ...], sorted by
    filename for reproducible ordering.
    """
    docs = []
    for path in sorted(corpus_dir.glob("*.md")):
        docs.append({"doc": path.name, "text": path.read_text(encoding="utf-8")})
    if not docs:
        raise FileNotFoundError(f"No .md files found in {corpus_dir}")
    return docs


def chunk_documents(docs: list[dict], max_chars: int = MAX_CHUNK_CHARS) -> list[dict]:
    """Split each loaded document into paragraph-sized chunks.

    `docs` must be the output of load_corpus() (or share its shape: a list of
    {"doc": ..., "text": ...} dicts). Returns [{"doc": ..., "text": ...}, ...] - one
    entry per chunk, several chunks per input document.
    """
    chunks = []
    for doc in docs:
        for paragraph in _split_paragraphs(doc["text"]):
            for piece in _split_long_paragraph(paragraph, max_chars):
                chunks.append({"doc": doc["doc"], "text": piece})
    return chunks


def load_and_chunk(corpus_dir: Path = DEFAULT_CORPUS_DIR, max_chars: int = MAX_CHUNK_CHARS) -> list[dict]:
    """Convenience wrapper: load_corpus() followed by chunk_documents()."""
    return chunk_documents(load_corpus(corpus_dir), max_chars)


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Chunk the rag-knowledge-base corpus and print a summary.")
    ap.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS_DIR)
    ap.add_argument("--max-chars", type=int, default=MAX_CHUNK_CHARS)
    args = ap.parse_args(argv)

    chunks = load_and_chunk(args.corpus_dir, args.max_chars)
    by_doc: dict[str, int] = {}
    for c in chunks:
        by_doc[c["doc"]] = by_doc.get(c["doc"], 0) + 1
    print(f"{len(chunks)} chunks from {len(by_doc)} documents in {args.corpus_dir}:")
    for doc, count in sorted(by_doc.items()):
        print(f"  {doc}: {count} chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
