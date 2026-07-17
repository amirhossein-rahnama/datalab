import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest  # noqa: E402
import stats  # noqa: E402

def test_confidence_interval_low_less_than_high():
    low, high = stats.confidence_interval([0.8, 0.82, 0.79, 0.81])
    assert low < high

def test_confidence_interval_contains_mean():
    scores = [0.8, 0.82, 0.79, 0.81]
    low, high = stats.confidence_interval(scores)
    assert low <= sum(scores) / len(scores) <= high

def test_cohens_d_sign_correct():
    higher = [5, 6, 7, 8]
    lower = [1, 2, 3, 4]
    assert stats.cohens_d(higher, lower) > 0
    assert stats.cohens_d(lower, higher) < 0

def test_cohens_d_zero_for_identical_samples():
    assert stats.cohens_d([1, 2, 3], [1, 2, 3]) == pytest.approx(0.0)

def test_mean_std_basic():
    mean, std = stats.mean_std([1, 2, 3, 4, 5])
    assert mean == pytest.approx(3.0)
    assert std == pytest.approx(1.5811, abs=1e-3)
