"""Retrieve the top-k most relevant chunks for a query.

Scoring is cosine similarity between the query's TF-IDF vector and every chunk's
TF-IDF vector (both projected into the same vocabulary space by the index's fitted
vectorizer) - the standard scikit-learn-only way to do lexical retrieval without an
embeddings model.
"""
from __future__ import annotations

from sklearn.metrics.pairwise import cosine_similarity

from .index import RagIndex


def retrieve(index: RagIndex, query: str, k: int = 3) -> list[dict]:
    """Return the top-k chunks most similar to `query`, each carrying a similarity score.

    Args:
        index: a RagIndex built by index.build_index().
        query: the natural-language question to retrieve context for.
        k: how many chunks to return, ranked highest-score first.

    Returns:
        [{"doc": ..., "text": ..., "score": float}, ...], sorted by score descending.
        `score` is cosine similarity in [0, 1] (0 = no shared vocabulary at all, 1 =
        identical TF-IDF vector); it is not a probability and scores across different
        queries aren't directly comparable.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    query_vec = index.vectorizer.transform([query])
    scores = cosine_similarity(query_vec, index.matrix)[0]
    ranked_positions = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    top_positions = ranked_positions[:k]
    return [
        {
            "doc": index.chunks[i]["doc"],
            "text": index.chunks[i]["text"],
            "score": float(scores[i]),
        }
        for i in top_positions
    ]
