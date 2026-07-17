"""RAG pipeline — step 6: generate an answer from retrieved context.

Uses a lazy LLM call so this module doesn't hard-fail until credentials/deps
are set up. Wire up your provider of choice — check Context7 for the current
SDK API before implementing the call.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from retrieve import retrieve  # noqa: E402

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def build_prompt(query: str, hits: list[dict]) -> str:
    context = "\n\n".join(f"[{i + 1}] {h['text']}" for i, h in enumerate(hits))
    system_path = PROMPTS_DIR / "system.txt"
    system = system_path.read_text(encoding="utf-8") if system_path.exists() else ""
    return f"{system}\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"


def generate(query: str, top_k: int = 5) -> dict:
    """Retrieve then generate. TODO: wire up a real LLM call (see module docstring)."""
    hits = retrieve(query, top_k)
    prompt = build_prompt(query, hits)
    answer = "TODO: call your LLM provider with `prompt` and return the completion."
    return {"query": query, "prompt": prompt, "answer": answer, "sources": hits}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate a RAG answer for {{project}}")
    ap.add_argument("--query", required=True)
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args(argv)

    result = generate(args.query, args.top_k)
    print(result["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
