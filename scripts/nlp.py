#!/usr/bin/env python3
"""Text classification: a TF-IDF + logistic regression pipeline, cross-validated training,
and a prediction helper.

Only core deps (numpy, scikit-learn) are used, all importable at module scope, so this
module is fully testable offline -- no embedding model or vector database is involved (see
vectorstore.py for the retrieval half of the NLP/RAG toolkit).
"""
from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline


def build_text_classifier(
    max_features: int | None = 5000,
    ngram_range: tuple[int, int] = (1, 2),
    C: float = 1.0,
    max_iter: int = 1000,
) -> Pipeline:
    """Build an untrained TF-IDF + logistic regression text classification pipeline."""
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)),
            ("clf", LogisticRegression(C=C, max_iter=max_iter)),
        ]
    )


def train_text_classifier(texts, labels, cv: int = 5, **pipeline_kwargs) -> dict:
    """Cross-validate and fit a text classifier built by `build_text_classifier`.

    `cv` is capped at the smallest class count (minimum 2) so cross-validation never raises
    on tiny corpora -- e.g. requesting cv=5 with only 4 examples of the rarest class runs a
    4-fold cross-validation instead of erroring. If no class has at least 2 members,
    cross-validation is skipped entirely (the accuracy fields come back as NaN) but the
    pipeline is still fit on all the data.

    Returns {"pipeline": <fitted Pipeline>, "cv_accuracy_mean": float, "cv_accuracy_std": float}.
    """
    texts = list(texts)
    labels = list(labels)
    if len(texts) != len(labels):
        raise ValueError(f"texts and labels must be the same length ({len(texts)} != {len(labels)})")
    if not texts:
        raise ValueError("texts must not be empty")

    pipeline = build_text_classifier(**pipeline_kwargs)

    _, class_counts = np.unique(labels, return_counts=True)
    min_class_count = int(class_counts.min())

    if min_class_count >= 2:
        effective_cv = max(2, min(cv, min_class_count))
        scores = cross_val_score(pipeline, texts, labels, cv=effective_cv, scoring="accuracy")
        cv_accuracy_mean = float(np.mean(scores))
        cv_accuracy_std = float(np.std(scores))
    else:
        cv_accuracy_mean = float("nan")
        cv_accuracy_std = float("nan")

    pipeline.fit(texts, labels)
    return {
        "pipeline": pipeline,
        "cv_accuracy_mean": cv_accuracy_mean,
        "cv_accuracy_std": cv_accuracy_std,
    }


def predict_texts(pipeline: Pipeline, texts) -> list:
    """Predict one label per entry in `texts` using a fitted pipeline."""
    texts = list(texts)
    predictions = pipeline.predict(texts)
    return [p.item() if hasattr(p, "item") else p for p in predictions]
