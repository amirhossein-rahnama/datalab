import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest  # noqa: E402

pytest.importorskip("optuna")

import tune  # noqa: E402

def test_tune_random_forest_returns_params_and_finite_score():
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=100, n_features=6, n_informative=4, random_state=42)
    result = tune.tune("random_forest", X, y, n_trials=3)
    assert set(result) == {"best_params", "best_score", "best_estimator"}
    assert isinstance(result["best_params"], dict) and result["best_params"]
    assert math.isfinite(result["best_score"])
    assert hasattr(result["best_estimator"], "predict")

def test_tune_ridge_regression_path():
    from sklearn.datasets import make_regression
    X, y = make_regression(n_samples=100, n_features=6, n_informative=4, random_state=42)
    result = tune.tune("ridge", X, y, task="regression", n_trials=3, cv=3)
    assert "alpha" in result["best_params"]
    assert math.isfinite(result["best_score"])
    assert hasattr(result["best_estimator"], "predict")

def test_tune_unknown_model_raises_value_error():
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=40, n_features=4, random_state=42)
    with pytest.raises(ValueError):
        tune.tune("not_a_model", X, y, n_trials=2)

def test_tune_mismatched_task_raises_value_error():
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=40, n_features=4, random_state=42)
    with pytest.raises(ValueError):
        tune.tune("svc", X, y, task="regression", n_trials=2)

def test_supported_includes_required_families():
    for name in ("random_forest", "gradient_boosting", "svc", "svr", "logistic_regression", "ridge"):
        assert name in tune.SUPPORTED
