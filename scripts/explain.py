#!/usr/bin/env python3
"""Model explainability: feature importance, SHAP summary (optional), and subgroup
(fairness) performance.

`shap` is a heavy optional dependency and is imported lazily inside `shap_summary` only,
so importing this module never fails if `shap` isn't installed.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

_METRIC_FUNCS = {
    "accuracy": accuracy_score,
    "precision": precision_score,
    "recall": recall_score,
    "f1": f1_score,
}


def feature_importance(model, feature_names=None) -> dict:
    """Feature name -> importance, from `model.feature_importances_` or `abs(model.coef_)`.

    For multi-class linear models (`coef_` with shape (n_classes, n_features)), the
    per-class absolute coefficients are averaged down to one value per feature.
    """
    if hasattr(model, "feature_importances_"):
        values = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        coef = np.asarray(model.coef_, dtype=float)
        values = np.abs(coef).mean(axis=0) if coef.ndim > 1 else np.abs(coef)
    else:
        raise ValueError("model has neither 'feature_importances_' nor 'coef_'")

    names = list(feature_names) if feature_names is not None else [f"f{i}" for i in range(len(values))]
    if len(names) != len(values):
        raise ValueError(f"feature_names length ({len(names)}) != importances length ({len(values)})")
    return {name: float(v) for name, v in zip(names, values)}


def shap_summary(model, X) -> dict:
    """Mean absolute SHAP value per feature. Requires the optional `shap` package."""
    try:
        import shap
    except ImportError as exc:
        raise ImportError(
            "shap_summary requires the 'shap' package. Install it with: pip install shap"
        ) from exc

    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)
    values = np.asarray(shap_values.values)
    mean_abs = np.abs(values).mean(axis=0)
    if mean_abs.ndim > 1:  # multi-class output: average across the class axis too
        mean_abs = mean_abs.mean(axis=-1)

    feature_names = list(getattr(X, "columns", range(len(mean_abs))))
    return {"mean_abs_shap": {str(name): float(v) for name, v in zip(feature_names, mean_abs)}}


def subgroup_performance(y_true, y_pred, groups, metric="accuracy") -> dict:
    """Per-subgroup score plus `max_gap`, the largest pairwise gap between subgroups
    (a simple fairness check)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    groups = np.asarray(groups)

    scorer = _METRIC_FUNCS.get(metric)
    if scorer is None:
        raise ValueError(f"unknown metric: {metric!r}. choose from {sorted(_METRIC_FUNCS)}")

    scores = {}
    for group in sorted(set(groups.tolist()), key=str):
        mask = groups == group
        scores[group] = float(scorer(y_true[mask], y_pred[mask]))

    max_gap = float(max(scores.values()) - min(scores.values())) if scores else 0.0
    return {"scores": scores, "max_gap": max_gap}
