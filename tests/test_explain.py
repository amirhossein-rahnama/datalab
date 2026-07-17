import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest  # noqa: E402
import explain  # noqa: E402

def test_subgroup_performance_returns_scores_and_max_gap():
    y_true = [1, 0, 1, 0, 1, 0, 1, 0]
    y_pred = [1, 0, 1, 0, 0, 0, 0, 0]
    groups = ["A", "A", "A", "A", "B", "B", "B", "B"]
    result = explain.subgroup_performance(y_true, y_pred, groups)
    assert set(result["scores"]) == {"A", "B"}
    assert result["scores"]["A"] == pytest.approx(1.0)
    assert result["scores"]["B"] == pytest.approx(0.5)
    assert result["max_gap"] == pytest.approx(0.5)

def test_subgroup_performance_zero_gap_when_equal():
    y_true = [1, 0, 1, 0]
    y_pred = [1, 0, 1, 0]
    groups = ["A", "A", "B", "B"]
    result = explain.subgroup_performance(y_true, y_pred, groups)
    assert result["max_gap"] == pytest.approx(0.0)

def test_feature_importance_from_feature_importances_attr():
    class FakeModel:
        feature_importances_ = [0.1, 0.7, 0.2]
    result = explain.feature_importance(FakeModel(), feature_names=["a", "b", "c"])
    assert result == pytest.approx({"a": 0.1, "b": 0.7, "c": 0.2})

def test_feature_importance_from_coef_attr_uses_default_names():
    class FakeModel:
        coef_ = [0.5, -0.3]
    result = explain.feature_importance(FakeModel())
    assert result["f0"] == pytest.approx(0.5)
    assert result["f1"] == pytest.approx(0.3)
