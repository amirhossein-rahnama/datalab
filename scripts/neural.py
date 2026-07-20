#!/usr/bin/env python3
"""Neural-net baselines: a leakage-safe sklearn MLP pipeline (core dep, fully testable),
plus a PyTorch tabular-net template for users who want real deep learning.

Only core deps (numpy, scikit-learn) are used at module scope. `torch_tabular_template`
returns training code as a plain string and never imports torch itself -- see its
docstring for the upgrade path from the sklearn MLP baseline to a real PyTorch model.
"""
from __future__ import annotations

import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def mlp_baseline(X, y, task="classification", cv=5, random_state=42) -> dict:
    """Cross-validated MLP baseline: a leakage-safe `Pipeline(StandardScaler -> MLP)`.

    `task` is "classification" (MLPClassifier) or "regression" (MLPRegressor). Scaling is
    fit inside each cross-validation fold via the pipeline, so no information from the
    validation fold leaks into training. Returns the per-fold `cross_val_score` mean/std
    and the (unfitted) pipeline used, so a caller can refit it on the full data once the
    baseline looks reasonable.
    """
    if task == "classification":
        estimator = MLPClassifier(
            hidden_layer_sizes=(64, 32), max_iter=500, random_state=random_state
        )
    elif task == "regression":
        estimator = MLPRegressor(
            hidden_layer_sizes=(64, 32), max_iter=500, random_state=random_state
        )
    else:
        raise ValueError(f"unknown task: {task!r}. choose 'classification' or 'regression'")

    pipeline = Pipeline([("scale", StandardScaler()), ("mlp", estimator)])
    scores = cross_val_score(pipeline, X, y, cv=cv)
    return {
        "cv_score_mean": float(np.mean(scores)),
        "cv_score_std": float(np.std(scores)),
        "pipeline": pipeline,
    }


def torch_tabular_template() -> str:
    """Return (as a string, not executed) a minimal PyTorch training template for a
    tabular feed-forward net, for users who want real deep learning beyond the sklearn
    MLP baseline above.

    This module never imports torch; the returned text is a starting point for the caller
    to save to a .py file and run in an environment where torch is installed.
    """
    return '''# Minimal PyTorch tabular-net training template.
# Requires: pip install torch
#
# This is a starting point, not a drop-in function -- adjust input_dim, output_dim, and
# the loss function for your task (nn.CrossEntropyLoss for classification, nn.MSELoss for
# regression). Compare against neural.mlp_baseline() before committing to the extra
# complexity of a hand-rolled torch model.

import torch
from torch import nn


class TabularNet(nn.Module):
    def __init__(self, input_dim, output_dim, hidden=(64, 32)):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU()]
            prev = h
        layers.append(nn.Linear(prev, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def train(X_train, y_train, input_dim, output_dim, epochs=100, lr=1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TabularNet(input_dim, output_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()  # swap for nn.MSELoss() on a regression task

    X = torch.as_tensor(X_train, dtype=torch.float32, device=device)
    y = torch.as_tensor(y_train, dtype=torch.long, device=device)

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(X)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer.step()

    return model
'''
