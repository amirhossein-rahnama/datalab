#!/usr/bin/env python3
"""Standardized diagnostic plots: confusion matrix, learning curve, ROC, residuals.

Uses the Agg backend so it works headlessly (no display required); every plotting
function saves a PNG to the given path and returns that path.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

from pathlib import Path  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import auc, confusion_matrix, roc_curve  # noqa: E402


def save_fig(fig, path) -> Path:
    """Save a matplotlib Figure to `path` (creating parent directories) and close it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return path


def plot_confusion_matrix(y_true, y_pred, path) -> Path:
    """Confusion-matrix heatmap saved to `path`."""
    labels = sorted(set(np.asarray(y_true).tolist()) | set(np.asarray(y_pred).tolist()), key=str)
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion Matrix")
    threshold = cm.max() / 2 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, str(cm[i, j]), ha="center", va="center",
                color="white" if cm[i, j] > threshold else "black",
            )
    fig.colorbar(im, ax=ax)
    return save_fig(fig, path)


def plot_learning_curve(train_sizes, train_scores, val_scores, path) -> Path:
    """Learning-curve plot (mean +/- std bands) saved to `path`.

    `train_scores`/`val_scores` may be 1D (one score per size) or 2D
    (size x cv-fold, as returned by `sklearn.model_selection.learning_curve`).
    """
    train_scores = np.asarray(train_scores, dtype=float)
    val_scores = np.asarray(val_scores, dtype=float)
    train_mean = train_scores.mean(axis=1) if train_scores.ndim > 1 else train_scores
    train_std = train_scores.std(axis=1) if train_scores.ndim > 1 else np.zeros_like(train_mean)
    val_mean = val_scores.mean(axis=1) if val_scores.ndim > 1 else val_scores
    val_std = val_scores.std(axis=1) if val_scores.ndim > 1 else np.zeros_like(val_mean)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(train_sizes, train_mean, "o-", label="Training score", color="#1f77b4")
    ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.15, color="#1f77b4")
    ax.plot(train_sizes, val_mean, "o-", label="Validation score", color="#ff7f0e")
    ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.15, color="#ff7f0e")
    ax.set_xlabel("Training examples")
    ax.set_ylabel("Score")
    ax.set_title("Learning Curve")
    ax.legend(loc="best")
    return save_fig(fig, path)


def plot_roc(y_true, y_score, path) -> Path:
    """ROC curve (with AUC in the legend) saved to `path`."""
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(fpr, tpr, color="#1f77b4", label=f"ROC curve (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", label="Chance")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve")
    ax.legend(loc="lower right")
    return save_fig(fig, path)


def plot_residuals(y_true, y_pred, path) -> Path:
    """Residuals-vs-predicted scatter plot saved to `path`."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residuals = y_true - y_pred

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(y_pred, residuals, alpha=0.6, color="#1f77b4")
    ax.axhline(0, color="red", linestyle="--")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Residual (true - predicted)")
    ax.set_title("Residual Plot")
    return save_fig(fig, path)
