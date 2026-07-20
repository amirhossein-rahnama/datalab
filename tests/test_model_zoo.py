import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest  # noqa: E402
import model_zoo  # noqa: E402

def test_bake_off_classification_returns_ranked_nonempty_list():
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=100, n_features=6, n_informative=4, random_state=42)
    results = model_zoo.bake_off(X, y, task="classification", cv=3)
    assert len(results) > 0
    for r in results:
        assert set(r) == {"name", "mean", "std"}
    means = [r["mean"] for r in results]
    assert means == sorted(means, reverse=True)

def test_best_model_returns_top_ranked_name():
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=100, n_features=6, n_informative=4, random_state=42)
    results = model_zoo.bake_off(X, y, task="classification", cv=3)
    top = model_zoo.best_model(results)
    assert isinstance(top, str)
    assert top in {r["name"] for r in results}
    assert top == results[0]["name"]

def test_bake_off_regression_returns_ranked_nonempty_list():
    from sklearn.datasets import make_regression
    X, y = make_regression(n_samples=100, n_features=6, n_informative=4, random_state=42)
    results = model_zoo.bake_off(X, y, task="regression", cv=3)
    assert len(results) > 0
    for r in results:
        assert set(r) == {"name", "mean", "std"}
    means = [r["mean"] for r in results]
    assert means == sorted(means, reverse=True)

def test_leaderboard_markdown_contains_pipe_table():
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=100, n_features=6, n_informative=4, random_state=42)
    results = model_zoo.bake_off(X, y, task="classification", cv=3)
    md = model_zoo.leaderboard_markdown(results)
    lines = md.splitlines()
    assert lines[0].startswith("|")
    assert "---" in lines[1]
    assert results[0]["name"] in md

def test_best_model_raises_on_empty_results():
    with pytest.raises(ValueError):
        model_zoo.best_model([])
