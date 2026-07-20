import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import neural  # noqa: E402

def test_mlp_baseline_classification_returns_score_in_unit_interval():
    from sklearn.datasets import make_classification

    X, y = make_classification(
        n_samples=60, n_features=5, n_informative=3, n_redundant=0, random_state=0
    )
    result = neural.mlp_baseline(X, y, task="classification", cv=3, random_state=0)

    assert set(result) == {"cv_score_mean", "cv_score_std", "pipeline"}
    assert isinstance(result["cv_score_mean"], float)
    assert 0.0 <= result["cv_score_mean"] <= 1.0
    assert isinstance(result["cv_score_std"], float)
    assert result["pipeline"].named_steps["mlp"].__class__.__name__ == "MLPClassifier"

def test_mlp_baseline_regression_returns_float_score():
    from sklearn.datasets import make_regression

    X, y = make_regression(n_samples=60, n_features=5, noise=0.1, random_state=0)
    result = neural.mlp_baseline(X, y, task="regression", cv=3, random_state=0)

    assert isinstance(result["cv_score_mean"], float)
    assert isinstance(result["cv_score_std"], float)
    assert result["pipeline"].named_steps["mlp"].__class__.__name__ == "MLPRegressor"

def test_mlp_baseline_unknown_task_raises():
    import numpy as np

    X = np.zeros((10, 2))
    y = np.zeros(10)
    try:
        neural.mlp_baseline(X, y, task="not_a_task")
        assert False, "expected ValueError for unknown task"
    except ValueError:
        pass

def test_torch_tabular_template_returns_nonempty_string_mentioning_torch():
    template = neural.torch_tabular_template()
    assert isinstance(template, str)
    assert len(template) > 0
    assert "torch" in template
    assert "pip install torch" in template
