#!/usr/bin/env python3
"""In-memory vector store and cosine-similarity retrieval for RAG.

`VectorStore` and its cosine-similarity search are pure numpy -- no embedding model,
database, or ANN index library is required -- so they are fully testable offline against
hand-made vectors. Only `embed_texts` (and `build_store_from_texts`, which calls it) needs
the optional `sentence-transformers` package, and that import is lazy, so importing this
module, and using `VectorStore` directly with precomputed vectors, never requires the
genai extra.
"""
from __future__ import annotations

import numpy as np


class VectorStore:
    """A minimal in-memory vector store with cosine-similarity search.

    Vectors and their metadata are supplied by the caller (e.g. via `embed_texts` /
    `build_store_from_texts`, or from any other embedding source) and kept in memory as
    plain numpy arrays -- there is no persistence, indexing, or external service involved.
    """

    def __init__(self) -> None:
        self._vectors: np.ndarray | None = None
        self._metadatas: list[dict] = []

    def __len__(self) -> int:
        return len(self._metadatas)

    def add(self, vectors: np.ndarray, metadatas: list[dict]) -> None:
        """Append `vectors` (shape (n, dim), or (dim,) for a single vector) and their
        parallel `metadatas` to the store."""
        vectors = np.asarray(vectors, dtype=float)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if len(vectors) != len(metadatas):
            raise ValueError(
                f"vectors and metadatas must be the same length ({len(vectors)} != {len(metadatas)})"
            )
        if self._vectors is None:
            self._vectors = vectors
        else:
            if vectors.shape[1] != self._vectors.shape[1]:
                raise ValueError(
                    f"vector dimension mismatch: store has {self._vectors.shape[1]}, got {vectors.shape[1]}"
                )
            self._vectors = np.vstack([self._vectors, vectors])
        self._metadatas.extend(metadatas)

    def search(self, query_vector: np.ndarray, k: int = 3) -> list[dict]:
        """Return the top-`k` stored entries most similar to `query_vector` by cosine
        similarity, highest score first, as a list of {"score": float, "metadata": dict}.

        Returns an empty list if the store has nothing in it yet.
        """
        if self._vectors is None or len(self._metadatas) == 0:
            return []
        query_vector = np.asarray(query_vector, dtype=float).reshape(-1)
        scores = _cosine_similarity(self._vectors, query_vector)
        top_k = max(0, min(k, len(scores)))
        order = np.argsort(-scores)[:top_k]
        return [{"score": float(scores[i]), "metadata": self._metadatas[i]} for i in order]


def _cosine_similarity(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """Cosine similarity between each row of `matrix` and `vector`, computed with plain
    numpy (dot product over the product of L2 norms). A zero-norm row or query scores 0.0
    instead of raising a division-by-zero warning.
    """
    matrix_norms = np.linalg.norm(matrix, axis=1)
    vector_norm = np.linalg.norm(vector)
    denom = matrix_norms * vector_norm
    numerator = matrix @ vector
    with np.errstate(invalid="ignore", divide="ignore"):
        scores = np.where(denom > 0, numerator / denom, 0.0)
    return scores


def embed_texts(texts, model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """Embed `texts` into dense vectors using a sentence-transformers model.

    Requires the optional `sentence-transformers` package (the "genai" extra). The import
    is lazy so importing this module never fails without it. Install with:
        python scripts/setup.py --genai
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "embed_texts requires the 'sentence-transformers' package. "
            "Install it with: python scripts/setup.py --genai "
            "(or by hand: pip install sentence-transformers)"
        ) from exc

    model = SentenceTransformer(model_name)
    embeddings = model.encode(list(texts))
    return np.asarray(embeddings, dtype=float)


def build_store_from_texts(texts, metadatas, model_name: str = "all-MiniLM-L6-v2") -> VectorStore:
    """Embed `texts` with `embed_texts` and load the results into a new VectorStore.

    This needs the optional genai extra (sentence-transformers) -- see `embed_texts`.
    `metadatas` must be the same length as `texts`; each entry is typically a dict carrying
    at least the source text, e.g. {"text": texts[i]}.
    """
    texts = list(texts)
    if len(texts) != len(metadatas):
        raise ValueError(f"texts and metadatas must be the same length ({len(texts)} != {len(metadatas)})")
    vectors = embed_texts(texts, model_name=model_name)
    store = VectorStore()
    store.add(vectors, metadatas)
    return store
