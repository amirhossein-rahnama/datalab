import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sklearn.pipeline import Pipeline  # noqa: E402
import nlp  # noqa: E402

BILLING_DOCS = [
    "Your invoice payment is past due, please update your billing details",
    "We could not process your credit card charge for this month's subscription",
    "The refund for your last invoice has been issued back to your account",
    "Please review your billing statement for unexpected subscription charges",
]

WEATHER_DOCS = [
    "Heavy rain and thunderstorms are expected across the region this afternoon",
    "Tomorrow will be sunny with a light breeze and mild temperatures",
    "A winter storm warning is in effect with several inches of snow forecast",
    "Expect foggy conditions in the morning clearing up by midday",
]


def _corpus():
    texts = BILLING_DOCS + WEATHER_DOCS
    labels = ["billing"] * len(BILLING_DOCS) + ["weather"] * len(WEATHER_DOCS)
    return texts, labels


def test_build_text_classifier_returns_tfidf_logreg_pipeline():
    pipeline = nlp.build_text_classifier()
    assert isinstance(pipeline, Pipeline)
    assert [name for name, _ in pipeline.steps] == ["tfidf", "clf"]
    assert pipeline.named_steps["clf"].max_iter == 1000


def test_train_text_classifier_returns_expected_keys_and_ranges():
    texts, labels = _corpus()
    result = nlp.train_text_classifier(texts, labels, cv=5)

    assert set(result) == {"pipeline", "cv_accuracy_mean", "cv_accuracy_std"}
    assert isinstance(result["pipeline"], Pipeline)
    assert isinstance(result["cv_accuracy_mean"], float)
    assert 0.0 <= result["cv_accuracy_mean"] <= 1.0
    assert isinstance(result["cv_accuracy_std"], float)
    assert result["cv_accuracy_std"] >= 0.0


def test_predict_texts_returns_one_label_per_input():
    texts, labels = _corpus()
    result = nlp.train_text_classifier(texts, labels, cv=5)

    new_texts = [
        "Can you update the credit card on file for my subscription invoice",
        "Will it snow overnight with strong wind gusts and freezing rain",
        "My last billing charge looks wrong, please issue a refund",
    ]
    predictions = nlp.predict_texts(result["pipeline"], new_texts)

    assert len(predictions) == len(new_texts)
    assert set(predictions) <= {"billing", "weather"}
