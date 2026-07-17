#!/usr/bin/env python3
"""Model diagnostics: fit classification (over/underfitting), cross-validation, baseline
comparison, class-imbalance detection, and error analysis.

Only core deps (pandas, numpy, scikit-learn) are used, all importable at module scope.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score


def classify_fit(train_score, val_score, gap_threshold=0.1, low_threshold=0.6) -> str:
    """Classify a model's fit from its train/validation scores.

    "overfitting" if the train-val gap exceeds `gap_threshold` and the train score is at
    least `low_threshold`; "underfitting" if both scores are below `low_threshold`;
    otherwise "good_fit".
    """
    gap = train_score - val_score
    if gap > gap_threshold and train_score >= low_threshold:
        return "overfitting"
    if train_score < low_threshold and val_score < low_threshold:
        return "underfitting"
    return "good_fit"


def cross_validate_summary(model, X, y, cv=5, scoring=None) -> dict:
    """Run sklearn `cross_val_score` and summarize the fold scores."""
    scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
    return {
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
        "scores": [float(s) for s in scores],
    }


def baseline_comparison(model, X, y, task="classification") -> dict:
    """Fit `model` and a matching sklearn Dummy baseline on (X, y); compare their scores.

    Uses each estimator's default `.score()` (accuracy for classifiers, R^2 for regressors).
    """
    if task == "classification":
        baseline = DummyClassifier(strategy="most_frequent")
    else:
        baseline = DummyRegressor(strategy="mean")
    model.fit(X, y)
    baseline.fit(X, y)
    model_score = float(model.score(X, y))
    baseline_score = float(baseline.score(X, y))
    return {
        "model_score": model_score,
        "baseline_score": baseline_score,
        "beats_baseline": bool(model_score > baseline_score),
    }


def detect_imbalance(y, threshold=0.2) -> dict:
    """Flag class imbalance: True when the smallest class fraction is below `threshold`."""
    counts = pd.Series(list(y)).value_counts(normalize=True)
    fractions = {}
    for key, value in counts.items():
        native_key = key.item() if hasattr(key, "item") else key
        fractions[native_key] = float(value)
    imbalanced = bool(counts.min() < threshold) if len(counts) else False
    return {"fractions": fractions, "imbalanced": imbalanced}


def error_analysis(y_true, y_pred, task="classification") -> dict:
    """Confusion matrix (classification) or residual stats (regression), plus worst-error
    indices (misclassifications, or the largest-magnitude residuals)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if task == "classification":
        labels = sorted(set(y_true.tolist()) | set(y_pred.tolist()), key=str)
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        worst = np.where(y_true != y_pred)[0].tolist()
        return {"confusion_matrix": cm.tolist(), "labels": labels, "worst_error_indices": worst}

    residuals = y_true - y_pred
    abs_residuals = np.abs(residuals)
    order = np.argsort(-abs_residuals)
    worst = order[: min(10, len(order))].tolist()
    return {
        "residual_mean": float(residuals.mean()) if residuals.size else 0.0,
        "residual_std": float(residuals.std()) if residuals.size else 0.0,
        "max_abs_error": float(abs_residuals.max()) if abs_residuals.size else 0.0,
        "worst_error_indices": worst,
    }
