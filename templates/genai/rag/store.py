"""RAG pipeline — step 4: vector store (Chroma by default).

chromadb is imported lazily so this module doesn't hard-fail until the
+genai tier's dependencies are installed. Swap for FAISS if you prefer a
purely local, dependency-light index — see the commented alternative below.
"""
from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_COLLECTION = "{{pkg}}_docs"
DEFAULT_PERSIST_DIR = "data/processed/chroma"


def _chromadb():
    try:
        import chromadb
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError("chromadb is required. Install it with: pip install chromadb") from exc
    return chromadb


def get_collection(persist_dir: str = DEFAULT_PERSIST_DIR, collection_name: str = DEFAULT_COLLECTION):
    chromadb = _chromadb()
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_or_create_collection(collection_name)


def upsert_chunks(
    chunks: list[dict], persist_dir: str = DEFAULT_PERSIST_DIR, collection_name: str = DEFAULT_COLLECTION
) -> None:
    """Each chunk needs 'text', 'embedding', 'source', 'chunk_id' (see embed.py)."""
    collection = get_collection(persist_dir, collection_name)
    collection.upsert(
        ids=[f"{c['source']}::{c['chunk_id']}" for c in chunks],
        embeddings=[c["embedding"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "chunk_id": c["chunk_id"]} for c in chunks],
    )


# --- FAISS alternative (uncomment and `pip install faiss-cpu` if preferred) ---
# import faiss
# import numpy as np
#
# def build_faiss_index(chunks: list[dict]):
#     vectors = np.array([c["embedding"] for c in chunks]).astype("float32")
#     index = faiss.IndexFlatL2(vectors.shape[1])
#     index.add(vectors)
#     return index


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Manage the {{project}} vector store")
    ap.add_argument("--persist-dir", default=DEFAULT_PERSIST_DIR)
    ap.add_argument("--collection", default=DEFAULT_COLLECTION)
    args = ap.parse_args(argv)
    Path(args.persist_dir).mkdir(parents=True, exist_ok=True)
    print(f"[store] collection={args.collection} persist_dir={args.persist_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
