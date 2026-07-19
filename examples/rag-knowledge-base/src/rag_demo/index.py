"""Build a TF-IDF index over corpus chunks.

This is the "retrieval" half of RAG, done entirely with scikit-learn's
TfidfVectorizer (a core dep) so the example runs offline: no embeddings API, no
vector database, no API key. It is a real, working retrieval method (classic
bag-of-words + inverse-document-frequency weighting), just not a neural one.

Usage:
    from rag_demo.chunk import load_and_chunk
    from rag_demo.index import build_index

    chunks = load_and_chunk()
    index = build_index(chunks)  # RagIndex, ready for retrieve()
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class RagIndex:
    """A fitted TF-IDF index over a list of chunks (as produced by chunk.py).

    Attributes:
        chunks: the original chunk dicts ({"doc": ..., "text": ...}), in the same
            order as the rows of `matrix` - row i of `matrix` is the TF-IDF vector
            for `chunks[i]["text"]`.
        vectorizer: the fitted TfidfVectorizer, reused to transform incoming queries
            into the same vector space (see retrieve.py).
        matrix: the fitted TF-IDF matrix, shape (n_chunks, n_vocabulary), a sparse
            scipy matrix.
    """

    chunks: list[dict]
    vectorizer: TfidfVectorizer
    matrix: Any


def build_index(chunks: list[dict]) -> RagIndex:
    """Fit a TfidfVectorizer over chunk texts and return the fitted index.

    Uses English stop-word removal so common words (the, is, and, ...) don't dilute
    the similarity signal between short support-doc chunks.
    """
    if not chunks:
        raise ValueError("chunks must be non-empty - did load_and_chunk() find any .md files?")
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    return RagIndex(chunks=chunks, vectorizer=vectorizer, matrix=matrix)
