"""RAG pipeline - step 5: retrieve the top-k relevant chunks for a query."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from embed import get_embedder  # noqa: E402
from store import get_collection  # noqa: E402

DEFAULT_TOP_K = 5


def retrieve(query: str, top_k: int = DEFAULT_TOP_K, persist_dir: str = "data/processed/chroma") -> list[dict]:
    embedder = get_embedder()
    collection = get_collection(persist_dir)
    query_embedding = embedder.encode([query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    hits = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for text, meta, distance in zip(documents, metadatas, distances):
        hits.append({"text": text, "metadata": meta, "distance": distance})
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Retrieve relevant chunks for a query in {{project}}")
    ap.add_argument("--query", required=True)
    ap.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    args = ap.parse_args(argv)

    hits = retrieve(args.query, args.top_k)
    for i, hit in enumerate(hits, 1):
        print(f"[{i}] (dist={hit['distance']:.4f}) {hit['metadata']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
