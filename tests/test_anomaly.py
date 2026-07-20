import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import numpy as np  # noqa: E402
import pytest  # noqa: E402
import anomaly  # noqa: E402


def _blob_with_outliers(n_normal=190, n_outliers=10, seed=42):
    rng = np.random.RandomState(seed)
    normal = rng.normal(loc=0.0, scale=1.0, size=(n_normal, 2))
    outliers = rng.uniform(low=15.0, high=25.0, size=(n_outliers, 2))
    X = np.vstack([normal, outliers])
    outlier_indices = np.arange(n_normal, n_normal + n_outliers)
    return X, outlier_indices


def _check_flags_injected_outliers(method):
    n_normal, n_outliers = 190, 10
    X, outlier_indices = _blob_with_outliers(n_normal, n_outliers)
    contamination = n_outliers / (n_normal + n_outliers)

    result = anomaly.detect_anomalies(X, method=method, contamination=contamination, random_state=42)

    assert set(result) == {"labels", "scores", "n_anomalies"}
    assert len(result["labels"]) == len(X)
    assert len(result["scores"]) == len(X)

    # roughly the contamination fraction gets flagged (10 of 200 = 5%)
    assert abs(result["n_anomalies"] - n_outliers) <= 2

    # the clearly-injected far-away points are (mostly) the ones flagged
    flagged = set(np.where(result["labels"] == -1)[0].tolist())
    injected = set(outlier_indices.tolist())
    assert len(flagged & injected) >= int(0.7 * n_outliers)


def test_detect_anomalies_isolation_forest_flags_injected_outliers():
    _check_flags_injected_outliers("isolation_forest")


def test_detect_anomalies_lof_flags_injected_outliers():
    _check_flags_injected_outliers("lof")


def test_detect_anomalies_unknown_method_raises():
    X = np.random.RandomState(0).normal(size=(20, 2))
    with pytest.raises(ValueError):
        anomaly.detect_anomalies(X, method="bogus")
