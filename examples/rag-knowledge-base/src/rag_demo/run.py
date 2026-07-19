"""End-to-end RAG demo: build a TF-IDF index over corpus/, run sample queries, and
print the top retrieved doc + score + the assembled prompt for each.

This is an OFFLINE RETRIEVAL demo. It uses only core deps (pandas, numpy,
scikit-learn) -- no API key, no network call, no heavy/optional dependencies. The
"generation" step (generate.answer()) is an honest extractive stub; see
generate.py's module docstring for where a real LLM call would go.

Runnable directly, from any working directory:
    python examples/rag-knowledge-base/src/rag_demo/run.py

Or via datalab, from inside this project:
    cd examples/rag-knowledge-base
    /datalab:work
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the `rag_demo` package importable when this file is executed directly (e.g.
# `python .../rag_demo/run.py`), regardless of the caller's current working
# directory. Executing a file directly does not add its package's parent to
# sys.path automatically, and this file lives *inside* the rag_demo package, so
# `import rag_demo` would otherwise fail with ModuleNotFoundError.
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag_demo.chunk import DEFAULT_CORPUS_DIR, load_and_chunk  # noqa: E402
from rag_demo.generate import answer  # noqa: E402
from rag_demo.index import build_index  # noqa: E402

SAMPLE_QUERIES = [
    "How do I export my data?",
    "What are the API rate limits?",
]


def run(corpus_dir: Path = DEFAULT_CORPUS_DIR, queries: list[str] = SAMPLE_QUERIES, k: int = 3) -> None:
    chunks = load_and_chunk(corpus_dir)
    print(f"Loaded {len(chunks)} chunks from {len(list(corpus_dir.glob('*.md')))} documents in {corpus_dir}")
    index = build_index(chunks)
    print(f"Built TF-IDF index: {index.matrix.shape[0]} chunks x {index.matrix.shape[1]} vocabulary terms")

    for query in queries:
        result = answer(index, query, k=k)
        top = result["sources"][0]

        print("\n" + "=" * 72)
        print(f"Query: {query}")
        print(f"Top retrieved doc: {top['doc']}  (score={top['score']:.4f})")
        print(f"All top-{k} sources: " + ", ".join(f"{s['doc']}({s['score']:.3f})" for s in result["sources"]))
        print("-" * 72)
        print("Assembled prompt (this is what a real LLM call would receive):")
        print(result["prompt"])
        print("-" * 72)
        print("Stub answer (extractive -- verbatim top chunk, NOT a generated answer):")
        print(result["answer"])


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
