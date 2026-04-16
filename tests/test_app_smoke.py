from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_returns_200() -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200


def test_dashboard_contains_phase_marker() -> None:
    response = client.get("/dashboard")

    assert "Скелет Phase 1 готов" in response.text
