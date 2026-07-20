import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import vectorstore  # noqa: E402


def test_search_returns_nearest_vector_metadata_first():
    store = vectorstore.VectorStore()
    vectors = np.array(
        [
            [1.0, 0.0, 0.0],  # unit vector along x
            [0.0, 1.0, 0.0],  # unit vector along y
            [0.0, 0.0, 1.0],  # unit vector along z
        ]
    )
    metadatas = [{"text": "x-axis"}, {"text": "y-axis"}, {"text": "z-axis"}]
    store.add(vectors, metadatas)

    query = np.array([0.9, 0.1, 0.0])  # closest to the x-axis vector
    results = store.search(query, k=2)

    assert len(results) == 2
    assert set(results[0]) == {"score", "metadata"}
    assert results[0]["metadata"] == {"text": "x-axis"}
    assert results[0]["score"] > results[1]["score"]


def test_search_respects_k():
    store = vectorstore.VectorStore()
    store.add(np.eye(5), [{"id": i} for i in range(5)])

    results = store.search(np.array([1.0, 0.0, 0.0, 0.0, 0.0]), k=3)

    assert len(results) == 3
    assert results[0]["metadata"] == {"id": 0}


def test_search_on_empty_store_returns_empty_list():
    store = vectorstore.VectorStore()
    assert store.search(np.array([1.0, 0.0]), k=3) == []


def test_add_accumulates_across_multiple_calls():
    store = vectorstore.VectorStore()
    store.add(np.array([[1.0, 0.0]]), [{"id": "a"}])
    store.add(np.array([[0.0, 1.0]]), [{"id": "b"}])

    assert len(store) == 2
    results = store.search(np.array([0.0, 1.0]), k=1)
    assert results[0]["metadata"] == {"id": "b"}
