#!/usr/bin/env python3
"""Multi-model bake-off: leakage-safe cross-validated comparison across a curated set of
scikit-learn models per task type, ranked best-first by mean CV score.

Only core deps (numpy, scikit-learn) are used, all importable at module scope. `xgboost` is
a heavy, optional dependency: it is detected lazily inside `bake_off` and, if importable,
XGBClassifier/XGBRegressor are folded into the comparison; if it isn't installed, they are
silently skipped (xgboost is a nice-to-have addition to the leaderboard, never a requirement
to run a bake-off).
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import Lasso, LogisticRegression, Ridge
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR

# Fixed so the bake-off is reproducible; not exposed as a bake_off() argument on purpose --
# every curated model that accepts a seed uses this one.
RANDOM_STATE = 42

# Model names that run on raw features. Every other curated (or extra) model is preceded by
# a StandardScaler fit inside the pipeline -- and therefore inside each CV fold, so no
# scaling statistic ever leaks from a validation fold into training.
_TREE_LIKE = {
    "RandomForestClassifier",
    "RandomForestRegressor",
    "GradientBoostingClassifier",
    "GradientBoostingRegressor",
    "XGBClassifier",
    "XGBRegressor",
}


def _classification_models() -> dict:
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "RandomForestClassifier": RandomForestClassifier(random_state=RANDOM_STATE),
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "SVC": SVC(random_state=RANDOM_STATE),
        "KNeighborsClassifier": KNeighborsClassifier(),
        "MLPClassifier": MLPClassifier(max_iter=500, random_state=RANDOM_STATE),
    }


def _regression_models() -> dict:
    return {
        "Ridge": Ridge(random_state=RANDOM_STATE),
        "Lasso": Lasso(random_state=RANDOM_STATE),
        "RandomForestRegressor": RandomForestRegressor(random_state=RANDOM_STATE),
        "GradientBoostingRegressor": GradientBoostingRegressor(random_state=RANDOM_STATE),
        "SVR": SVR(),
        "KNeighborsRegressor": KNeighborsRegressor(),
        "MLPRegressor": MLPRegressor(max_iter=500, random_state=RANDOM_STATE),
    }


def _xgboost_model(task):
    """Return an unfitted XGBoost estimator for `task` if `xgboost` is importable, else None.

    Never raises: xgboost is an optional leaderboard addition, not a requirement, so its
    absence just means the leaderboard has one or two fewer rows.
    """
    try:
        from xgboost import XGBClassifier, XGBRegressor
    except ImportError:
        return None
    if task == "classification":
        return XGBClassifier(random_state=RANDOM_STATE)
    return XGBRegressor(random_state=RANDOM_STATE)


def _wrap(name, model) -> Pipeline:
    """Wrap `model` in a leakage-safe Pipeline.

    Tree ensembles (`_TREE_LIKE`) run on raw features. Every other model -- the curated
    linear/SVM/KNN/MLP families, and any unrecognized `extra_models` entry -- is preceded by
    a StandardScaler so scaling helps where it matters and is still fit fresh inside every CV
    fold. Pass an already-built `Pipeline` in `extra_models` for full control instead.
    """
    if name in _TREE_LIKE:
        return Pipeline([("model", model)])
    return Pipeline([("scale", StandardScaler()), ("model", model)])


def bake_off(X, y, task="classification", cv=5, scoring=None, extra_models=None) -> list[dict]:
    """Cross-validate a curated set of scikit-learn models on (X, y) and rank them.

    Each model is wrapped in a `Pipeline` (see `_wrap`) so any preprocessing is fit only
    within each CV fold -- never on the full dataset before splitting. Scored with
    `cross_val_score` (default: accuracy for classification, r2 for regression; pass
    `scoring` to override with any scikit-learn scorer string).

    `extra_models` optionally adds/overrides entries: a mapping (or iterable of (name,
    estimator) pairs) of model name -> estimator or pre-built Pipeline.

    Returns a list of `{"name", "mean", "std"}` dicts, sorted best-first (highest mean
    score). `cross_val_score` treats every supported scorer as higher-is-better (built-in
    "neg_*" scorers are already sign-flipped), so a plain descending sort is always correct.
    """
    if task not in ("classification", "regression"):
        raise ValueError(f"task must be 'classification' or 'regression', got {task!r}")
    scoring = scoring if scoring is not None else ("accuracy" if task == "classification" else "r2")

    models = _classification_models() if task == "classification" else _regression_models()

    xgb_model = _xgboost_model(task)
    if xgb_model is not None:
        models["XGBClassifier" if task == "classification" else "XGBRegressor"] = xgb_model

    if extra_models:
        models.update(extra_models)

    results = []
    for name, model in models.items():
        pipeline = model if isinstance(model, Pipeline) else _wrap(name, model)
        scores = cross_val_score(pipeline, X, y, cv=cv, scoring=scoring)
        results.append({"name": name, "mean": float(np.mean(scores)), "std": float(np.std(scores))})

    results.sort(key=lambda r: r["mean"], reverse=True)
    return results


def best_model(results) -> str:
    """Return the name of the top-ranked model from `bake_off`'s (already ranked) output."""
    if not results:
        raise ValueError("results is empty; nothing to select from")
    return results[0]["name"]


def leaderboard_markdown(results) -> str:
    """Render `bake_off` results (already ranked) as a GitHub-style Markdown table."""
    lines = ["| Model | Mean | Std |", "| --- | --- | --- |"]
    for r in results:
        lines.append(f"| {r['name']} | {r['mean']:.4f} | {r['std']:.4f} |")
    return "\n".join(lines)
