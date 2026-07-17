"""RAG pipeline — step 2: chunk documents into retrieval-sized passages."""
from __future__ import annotations

import argparse

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    """Simple sliding-window character chunker.

    Swap for a token-aware splitter (e.g. langchain's
    RecursiveCharacterTextSplitter) once Context7 confirms the current API.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def chunk_documents(
    docs: list[dict], chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP
) -> list[dict]:
    """Each input doc needs a 'source' and 'text' key (see loader.py)."""
    chunks = []
    for doc in docs:
        for i, piece in enumerate(chunk_text(doc["text"], chunk_size, overlap)):
            chunks.append({"source": doc["source"], "chunk_id": i, "text": piece})
    return chunks


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Chunk loaded documents for {{project}}")
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    ap.add_argument("--overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    args = ap.parse_args(argv)
    print(f"[chunk] chunk_size={args.chunk_size} overlap={args.overlap} (wire this up to loader.py output)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
