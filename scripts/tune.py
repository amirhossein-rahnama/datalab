#!/usr/bin/env python3
"""Optuna hyperparameter search over a leakage-safe pipeline for a curated set of
scikit-learn model families.

Only core deps (numpy, scikit-learn) are used, all importable at module scope. `optuna` is a
heavy, optional dependency and is imported lazily inside `tune` only, so importing this
module never fails if `optuna` isn't installed.
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR

SUPPORTED = [
    "random_forest",
    "gradient_boosting",
    "svc",
    "svr",
    "logistic_regression",
    "ridge",
]

# Model names whose task is fixed regardless of the `task` argument (classification-only or
# regression-only estimators). "random_forest" / "gradient_boosting" are task-agnostic and
# switch between the Classifier/Regressor variant based on `task` instead.
_FIXED_TASK = {
    "svc": "classification",
    "svr": "regression",
    "logistic_regression": "classification",
    "ridge": "regression",
}

# Tree ensembles run on raw features; every other supported family is scaled (see _wrap).
_TREE_LIKE = {"random_forest", "gradient_boosting"}


def _base_estimator(model_name, task, random_state):
    """Return an unfitted estimator for `model_name`/`task`, seeded with `random_state`."""
    if model_name == "random_forest":
        cls = RandomForestClassifier if task == "classification" else RandomForestRegressor
        return cls(random_state=random_state)
    if model_name == "gradient_boosting":
        cls = GradientBoostingClassifier if task == "classification" else GradientBoostingRegressor
        return cls(random_state=random_state)
    if model_name == "svc":
        return SVC(random_state=random_state)
    if model_name == "svr":
        return SVR()  # SVR has no random_state parameter (deterministic solver)
    if model_name == "logistic_regression":
        return LogisticRegression(max_iter=1000, random_state=random_state)
    if model_name == "ridge":
        return Ridge(random_state=random_state)
    raise ValueError(f"unknown model_name: {model_name!r}. choose from {SUPPORTED}")


def _wrap(model_name, model) -> Pipeline:
    """Wrap `model` in a leakage-safe Pipeline (scaled unless it's a tree ensemble)."""
    if model_name in _TREE_LIKE:
        return Pipeline([("model", model)])
    return Pipeline([("scale", StandardScaler()), ("model", model)])


def _search_space(model_name, trial) -> dict:
    """Return a `{"model__<param>": value}` dict of Optuna-suggested hyperparameters.

    Every range here is chosen so that ANY combination of suggested values is a valid
    scikit-learn constructor call -- important because a low `n_trials` budget (as in a
    quick tuning run) may sample anywhere in the space, including on the first trial.
    """
    if model_name == "random_forest":
        return {
            "model__n_estimators": trial.suggest_int("n_estimators", 50, 300),
            "model__max_depth": trial.suggest_int("max_depth", 2, 20),
            "model__min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            "model__min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
        }
    if model_name == "gradient_boosting":
        return {
            "model__n_estimators": trial.suggest_int("n_estimators", 50, 300),
            "model__max_depth": trial.suggest_int("max_depth", 2, 10),
            "model__learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
            "model__subsample": trial.suggest_float("subsample", 0.6, 1.0),
        }
    if model_name in ("svc", "svr"):
        params = {
            "model__C": trial.suggest_float("C", 1e-3, 1e2, log=True),
            "model__gamma": trial.suggest_float("gamma", 1e-4, 1e1, log=True),
            "model__kernel": trial.suggest_categorical("kernel", ["rbf", "linear"]),
        }
        if model_name == "svr":
            params["model__epsilon"] = trial.suggest_float("epsilon", 1e-3, 1.0, log=True)
        return params
    if model_name == "logistic_regression":
        return {
            "model__C": trial.suggest_float("C", 1e-3, 1e2, log=True),
            "model__class_weight": trial.suggest_categorical("class_weight", [None, "balanced"]),
        }
    if model_name == "ridge":
        return {
            "model__alpha": trial.suggest_float("alpha", 1e-3, 1e3, log=True),
            "model__fit_intercept": trial.suggest_categorical("fit_intercept", [True, False]),
        }
    raise ValueError(f"unknown model_name: {model_name!r}. choose from {SUPPORTED}")


def tune(model_name, X, y, task="classification", n_trials=30, cv=5, timeout=None,
         random_state=42) -> dict:
    """Optuna hyperparameter search for one curated model family.

    Reuses the same leakage-safe Pipeline pattern as `model_zoo.bake_off` -- StandardScaler
    (fit fresh inside every CV fold) plus the model for every family except the tree
    ensembles, which run on raw features -- and scores with accuracy (classification) or r2
    (regression), matching `bake_off`'s defaults so the two are directly comparable.

    `model_name` must be one of `SUPPORTED`. "svc"/"svr" and "logistic_regression"/"ridge"
    are tied to one task each; "random_forest" and "gradient_boosting" work for both and
    switch estimator class based on `task`.

    Returns `{"best_params", "best_score", "best_estimator"}`: `best_params` is the winning
    trial's raw (unprefixed) hyperparameters, `best_score` is its mean CV score, and
    `best_estimator` is the winning pipeline refit on the full `(X, y)` passed in -- the
    artifact to persist, analogous to `GridSearchCV(refit=True).best_estimator_`.

    Requires the optional `optuna` package, imported lazily here (not at module scope).
    """
    try:
        import optuna
    except ImportError as exc:
        raise ImportError(
            "tune requires the 'optuna' package. Install it with: pip install optuna"
        ) from exc

    if task not in ("classification", "regression"):
        raise ValueError(f"task must be 'classification' or 'regression', got {task!r}")
    if model_name not in SUPPORTED:
        raise ValueError(f"unknown model_name: {model_name!r}. choose from {SUPPORTED}")
    fixed_task = _FIXED_TASK.get(model_name)
    if fixed_task is not None and fixed_task != task:
        raise ValueError(f"{model_name!r} only supports task={fixed_task!r}, got {task!r}")

    scoring = "accuracy" if task == "classification" else "r2"
    pipeline = _wrap(model_name, _base_estimator(model_name, task, random_state))

    def objective(trial) -> float:
        pipeline.set_params(**_search_space(model_name, trial))
        scores = cross_val_score(pipeline, X, y, cv=cv, scoring=scoring)
        return float(np.mean(scores))

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    sampler = optuna.samplers.TPESampler(seed=random_state)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=n_trials, timeout=timeout, show_progress_bar=False)

    best_estimator = _wrap(model_name, _base_estimator(model_name, task, random_state))
    best_estimator.set_params(**{f"model__{k}": v for k, v in study.best_params.items()})
    best_estimator.fit(X, y)

    return {
        "best_params": dict(study.best_params),
        "best_score": float(study.best_value),
        "best_estimator": best_estimator,
    }
