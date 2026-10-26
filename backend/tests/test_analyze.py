"""Regression tests for the ScamShield analysis endpoint."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import analyze as analyze_module

client = TestClient(app)


class FakeVectorizer:
    def transform(self, texts):
        return texts


class FakeClassifier:
    classes_ = ["BENIGN", "SCAM"]

    def predict(self, features):
        return ["SCAM"]

    def predict_proba(self, features):
        return [[0.1, 0.9]]


def test_analyze_message_returns_expected_fields():
    with (
        patch.object(analyze_module, "vectorizer", FakeVectorizer()),
        patch.object(analyze_module, "classifier", FakeClassifier()),
        patch.object(analyze_module, "analyze_text_urls", return_value=[]),
    ):
        response = client.post(
            "/api/v1/analyze",
            json={"message": "Verify your account immediately"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "SCAM"
    assert data["label"] == "SCAM"
    assert data["scam_score"] == 0.9
    assert data["scam_probability"] == 0.9
    assert data["risk_score"] == 90.0
    assert data["risk_level"] == "CRITICAL"
    assert isinstance(data["limitations"], list)


def test_analyze_rejects_empty_input():
    response = client.post("/api/v1/analyze", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Provide a message or URL to analyze."


def test_analyze_accepts_url_only():
    with (
        patch.object(analyze_module, "vectorizer", FakeVectorizer()),
        patch.object(analyze_module, "classifier", FakeClassifier()),
        patch.object(analyze_module, "analyze_text_urls", return_value=[]),
    ):
        response = client.post(
            "/api/v1/analyze",
            json={"url": "https://example.com"},
        )

    assert response.status_code == 200
    assert response.json()["prediction"] == "SCAM"


def test_analyze_hides_internal_errors():
    with (
        patch.object(analyze_module, "vectorizer", FakeVectorizer()),
        patch.object(analyze_module, "classifier", FakeClassifier()),
        patch.object(
            analyze_module,
            "analyze_text_urls",
            side_effect=RuntimeError("internal test detail"),
        ),
    ):
        response = client.post(
            "/api/v1/analyze",
            json={"message": "Please review this message"},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Analysis failed. Check the backend logs."


def test_risk_level_thresholds():
    assert analyze_module.get_risk_level(0) == "LOW"
    assert analyze_module.get_risk_level(24.99) == "LOW"
    assert analyze_module.get_risk_level(25) == "MEDIUM"
    assert analyze_module.get_risk_level(50) == "HIGH"
    assert analyze_module.get_risk_level(75) == "CRITICAL"
