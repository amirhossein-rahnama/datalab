#!/usr/bin/env python3
"""Lightweight statistics for reporting model results: confidence intervals, effect size,
and mean/std summaries. numpy + stdlib only - scipy is intentionally NOT required.
"""
from __future__ import annotations

import math

import numpy as np

# z-scores for common two-sided confidence levels (looked up instead of requiring scipy).
_Z_TABLE = {
    0.80: 1.282,
    0.85: 1.440,
    0.90: 1.645,
    0.95: 1.960,
    0.98: 2.326,
    0.99: 2.576,
}


def mean_std(scores) -> tuple[float, float]:
    """Return (mean, sample std with ddof=1) of `scores`."""
    arr = np.asarray(list(scores), dtype=float)
    if arr.size == 0:
        raise ValueError("scores must not be empty")
    mean = float(arr.mean())
    std = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
    return mean, std


def confidence_interval(scores, confidence: float = 0.95) -> tuple[float, float]:
    """Mean +/- z * SEM confidence interval, z from a lookup table of common confidence
    levels (nearest match), which avoids requiring scipy."""
    arr = np.asarray(list(scores), dtype=float)
    if arr.size == 0:
        raise ValueError("scores must not be empty")
    mean = float(arr.mean())
    if arr.size == 1:
        return mean, mean
    std = float(arr.std(ddof=1))
    sem = std / math.sqrt(arr.size)
    nearest = min(_Z_TABLE, key=lambda level: abs(level - confidence))
    margin = _Z_TABLE[nearest] * sem
    return mean - margin, mean + margin


def cohens_d(a, b) -> float:
    """Cohen's d effect size between two independent samples (pooled standard deviation)."""
    a = np.asarray(list(a), dtype=float)
    b = np.asarray(list(b), dtype=float)
    if a.size < 2 or b.size < 2:
        raise ValueError("cohens_d requires at least 2 observations in each sample")
    na, nb = a.size, b.size
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled_std = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if pooled_std == 0:
        return 0.0
    return float((a.mean() - b.mean()) / pooled_std)
