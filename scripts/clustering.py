#!/usr/bin/env python3
"""Clustering: internal validity metrics, silhouette-driven k selection, and a thin
fit_predict wrapper around KMeans.

Only core deps (numpy, scikit-learn) are used, all importable at module scope.
"""
from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)


def cluster_metrics(X, labels) -> dict:
    """Internal cluster-validity metrics for a labeling of `X`.

    Silhouette (higher is better, range [-1, 1]), Davies-Bouldin (lower is better), and
    Calinski-Harabasz (higher is better) all require at least 2 clusters and fewer clusters
    than samples. When `labels` has fewer than 2 distinct clusters, all three metrics are
    set to None rather than raising, and only `n_clusters` is meaningful.
    """
    X = np.asarray(X)
    labels = np.asarray(labels)
    n_clusters = int(len(np.unique(labels)))

    if n_clusters < 2:
        return {
            "silhouette": None,
            "davies_bouldin": None,
            "calinski_harabasz": None,
            "n_clusters": n_clusters,
        }

    return {
        "silhouette": float(silhouette_score(X, labels)),
        "davies_bouldin": float(davies_bouldin_score(X, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(X, labels)),
        "n_clusters": n_clusters,
    }


def auto_k(X, k_range=range(2, 11), random_state=42) -> dict:
    """Fit KMeans for each k in `k_range` and pick the best k by silhouette score.

    `scores` maps every k in `k_range` that produced at least 2 clusters to its silhouette
    score; `best_k` is the k with the highest score. Raises ValueError if no k in `k_range`
    produced a valid (>=2 cluster) labeling.
    """
    X = np.asarray(X)
    scores: dict = {}
    for k in k_range:
        labels = KMeans(n_clusters=k, random_state=random_state).fit_predict(X)
        if len(np.unique(labels)) < 2:
            continue
        scores[k] = float(silhouette_score(X, labels))

    if not scores:
        raise ValueError("no k in k_range produced at least 2 clusters")

    best_k = max(scores, key=lambda key: scores[key])
    return {"best_k": best_k, "scores": scores}


def fit_kmeans(X, k, random_state=42):
    """Fit sklearn KMeans with `k` clusters on `X`. Returns (model, labels)."""
    model = KMeans(n_clusters=k, random_state=random_state)
    labels = model.fit_predict(np.asarray(X))
    return model, labels
