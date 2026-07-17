import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest  # noqa: E402
import diagnostics  # noqa: E402

def test_classify_fit_overfitting():
    assert diagnostics.classify_fit(0.99, 0.70) == "overfitting"

def test_classify_fit_underfitting():
    assert diagnostics.classify_fit(0.55, 0.53) == "underfitting"

def test_classify_fit_good_fit():
    assert diagnostics.classify_fit(0.90, 0.88) == "good_fit"

def test_detect_imbalance_flags_95_5_split():
    y = [0] * 95 + [1] * 5
    result = diagnostics.detect_imbalance(y)
    assert result["imbalanced"] is True
    assert result["fractions"][0] == pytest.approx(0.95)
    assert result["fractions"][1] == pytest.approx(0.05)

def test_detect_imbalance_balanced_not_flagged():
    y = [0] * 50 + [1] * 50
    result = diagnostics.detect_imbalance(y)
    assert result["imbalanced"] is False

def test_cross_validate_summary_returns_mean_std_scores():
    from sklearn.datasets import make_classification
    from sklearn.linear_model import LogisticRegression
    X, y = make_classification(n_samples=100, n_features=4, random_state=0)
    result = diagnostics.cross_validate_summary(LogisticRegression(), X, y, cv=3)
    assert set(result) == {"mean", "std", "scores"}
    assert len(result["scores"]) == 3
    assert 0.0 <= result["mean"] <= 1.0

def test_baseline_comparison_beats_dummy_on_separable_data():
    from sklearn.datasets import make_classification
    from sklearn.linear_model import LogisticRegression
    X, y = make_classification(n_samples=200, n_features=4, random_state=0)
    result = diagnostics.baseline_comparison(LogisticRegression(), X, y, task="classification")
    assert set(result) == {"model_score", "baseline_score", "beats_baseline"}
    assert result["beats_baseline"] is True

def test_error_analysis_classification_confusion_matrix():
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 1, 1]
    result = diagnostics.error_analysis(y_true, y_pred, task="classification")
    assert "confusion_matrix" in result
    assert result["worst_error_indices"] == [1]

def test_error_analysis_regression_residuals():
    y_true = [1.0, 2.0, 3.0]
    y_pred = [1.1, 2.5, 2.9]
    result = diagnostics.error_analysis(y_true, y_pred, task="regression")
    assert "residual_mean" in result
    assert "worst_error_indices" in result
