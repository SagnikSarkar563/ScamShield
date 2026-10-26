"""Health endpoint contract tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    """The liveness endpoint returns the documented response."""
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
