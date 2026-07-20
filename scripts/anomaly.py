#!/usr/bin/env python3
"""Anomaly detection: Isolation Forest and Local Outlier Factor wrapped behind one
consistent {labels, scores, n_anomalies} contract.

Only core deps (numpy, scikit-learn) are used, all importable at module scope.
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


def detect_anomalies(X, method="isolation_forest", contamination=0.05, random_state=42) -> dict:
    """Flag outliers in `X` using `method` ("isolation_forest" or "lof").

    Returns sklearn-convention `labels` (1=normal, -1=anomaly), `scores` (higher means more
    normal, lower/more negative means more anomalous), and `n_anomalies` (count of -1
    labels). `random_state` only affects "isolation_forest" -- LocalOutlierFactor has no
    seed to set.
    """
    X = np.asarray(X)

    if method == "isolation_forest":
        model = IsolationForest(contamination=contamination, random_state=random_state)
        labels = model.fit_predict(X)
        scores = model.decision_function(X)
    elif method == "lof":
        model = LocalOutlierFactor(contamination=contamination)
        labels = model.fit_predict(X)
        scores = model.negative_outlier_factor_
    else:
        raise ValueError(f"Unknown method: {method!r}")

    labels = np.asarray(labels)
    scores = np.asarray(scores, dtype=float)
    return {
        "labels": labels,
        "scores": scores,
        "n_anomalies": int(np.sum(labels == -1)),
    }
