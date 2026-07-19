"""Generation step of the RAG pipeline -- currently a STUB.

Retrieval (chunk.py + index.py + retrieve.py) runs entirely offline with
scikit-learn's TfidfVectorizer, so everything up to this module works with zero API
keys and zero heavy/optional dependencies.

Real *generation* -- turning retrieved chunks into a fluent, synthesized answer --
needs an LLM call. That needs:
  1. An LLM client library, e.g. `pip install anthropic` (a separate, lightweight
     dependency -- NOT the same as datalab's `genai` tier deps in
     scripts/requirements-genai.txt, which cover embeddings/vector-store libraries
     for a *neural* retrieval path, not the generation call itself).
  2. An API key: `export ANTHROPIC_API_KEY=...`.

Neither is available in this example (core deps only, no network), so `answer()`
below never calls out to a real model. Instead it returns an honest *extractive*
stand-in -- literally the single highest-scoring retrieved chunk, not a paraphrase or
summary -- plus the exact prompt a real call would use, so you can see what
"grounded" means before any model or API key is involved. See the `# TODO: real
generation` block inside answer() for where the real call goes.
"""
from __future__ import annotations

from .index import RagIndex
from .retrieve import retrieve

SYSTEM_PROMPT = (
    "You are a support assistant for NimbusBoard, a project-tracking SaaS product. "
    "Answer the user's question using ONLY the context below. If the context does not "
    "contain the answer, say you don't know. Cite the source document(s) you used."
)


def build_prompt(query: str, hits: list[dict]) -> str:
    """Assemble a grounded prompt: system instructions + retrieved context + the question.

    This is exactly the prompt a real LLM call in answer() below would send. Printing
    it (see run.py) lets you inspect what "grounded" means before any model gets
    involved.
    """
    context = "\n\n".join(
        f"[{i + 1}] (from {hit['doc']}, score={hit['score']:.3f})\n{hit['text']}" for i, hit in enumerate(hits)
    )
    return f"{SYSTEM_PROMPT}\n\n--- Retrieved context ---\n{context}\n\n--- Question ---\n{query}\n\n--- Answer ---"


def answer(index: RagIndex, query: str, k: int = 3) -> dict:
    """Retrieve top-k chunks for `query`, assemble a grounded prompt, and return a stub answer.

    Args:
        index: a RagIndex built by index.build_index().
        query: the natural-language question to answer.
        k: how many chunks to retrieve as context.

    Returns:
        {"query": ..., "prompt": ..., "answer": ..., "sources": ...}:
          - "prompt" is the full grounded prompt a real LLM call would receive.
          - "answer" is an EXTRACTIVE stub: the text of the single top-scoring chunk
            verbatim, not a generated/synthesized answer. This is the honest thing to
            return without calling a model -- it is never invented text.
          - "sources" is the full list of retrieved chunks (doc name, text, score).
    """
    hits = retrieve(index, query, k=k)
    prompt = build_prompt(query, hits)

    # ---------------------------------------------------------------------------
    # TODO: real generation.
    #
    # Swap the extractive stub below for an actual Claude call once an LLM client
    # is installed (`pip install anthropic`) and ANTHROPIC_API_KEY is set:
    #
    #   import anthropic
    #   client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the env
    #   response = client.messages.create(
    #       model="claude-opus-4-8",
    #       max_tokens=1024,
    #       messages=[{"role": "user", "content": prompt}],
    #   )
    #   real_answer = next(b.text for b in response.content if b.type == "text")
    #
    # See https://docs.claude.com/en/api/messages for the current Messages API
    # surface (model IDs, parameters) before wiring this up for real.
    # ---------------------------------------------------------------------------
    extractive_answer = hits[0]["text"] if hits else "No relevant context found in the corpus."

    return {"query": query, "prompt": prompt, "answer": extractive_answer, "sources": hits}
