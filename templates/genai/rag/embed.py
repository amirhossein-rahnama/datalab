"""RAG pipeline - step 3: embed chunks.

sentence-transformers is imported lazily so this module doesn't hard-fail
until the +genai tier's dependencies are installed.
"""
from __future__ import annotations

import argparse

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


def _sentence_transformers():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "sentence-transformers is required for embeddings. "
            "Install it with: pip install sentence-transformers"
        ) from exc
    return SentenceTransformer


def get_embedder(model_name: str = DEFAULT_MODEL_NAME):
    SentenceTransformer = _sentence_transformers()
    return SentenceTransformer(model_name)


def embed_chunks(chunks: list[dict], model_name: str = DEFAULT_MODEL_NAME) -> list[dict]:
    """Add an 'embedding' field to each chunk dict (see chunk.py for chunk shape)."""
    embedder = get_embedder(model_name)
    texts = [c["text"] for c in chunks]
    vectors = embedder.encode(texts, show_progress_bar=False)
    return [{**chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Embed chunks for {{project}}")
    ap.add_argument("--model", default=DEFAULT_MODEL_NAME)
    args = ap.parse_args(argv)
    print(f"[embed] model={args.model} (wire this up to chunk.py output)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
