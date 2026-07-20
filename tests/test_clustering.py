import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import clustering  # noqa: E402
from sklearn.datasets import make_blobs  # noqa: E402


def _three_blobs():
    return make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=42)


def test_auto_k_picks_sensible_k_for_three_blobs():
    X, _ = _three_blobs()
    result = clustering.auto_k(X, k_range=range(2, 11), random_state=42)
    assert set(result) == {"best_k", "scores"}
    assert 2 <= result["best_k"] <= 5
    assert result["scores"][result["best_k"]] == max(result["scores"].values())


def test_cluster_metrics_positive_silhouette_for_true_labels():
    X, y = _three_blobs()
    result = clustering.cluster_metrics(X, y)
    assert set(result) == {"silhouette", "davies_bouldin", "calinski_harabasz", "n_clusters"}
    assert result["n_clusters"] == 3
    assert result["silhouette"] > 0


def test_cluster_metrics_skips_silhouette_below_two_clusters():
    X, _ = make_blobs(n_samples=50, centers=1, random_state=42)
    result = clustering.cluster_metrics(X, [0] * 50)
    assert result["n_clusters"] == 1
    assert result["silhouette"] is None
    assert result["davies_bouldin"] is None
    assert result["calinski_harabasz"] is None


def test_fit_kmeans_returns_fitted_model_and_labels():
    X, _ = _three_blobs()
    model, labels = clustering.fit_kmeans(X, 3, random_state=42)
    assert model.n_clusters == 3
    assert hasattr(model, "cluster_centers_")
    assert model.cluster_centers_.shape == (3, X.shape[1])
    assert len(labels) == len(X)
    assert len(set(labels.tolist())) == 3
