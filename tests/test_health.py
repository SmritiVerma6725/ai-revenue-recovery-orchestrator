from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard() -> None:
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.json()["revenue_at_risk"] == 2500000


def test_recovery_cases() -> None:
    response = client.get("/api/recovery-cases")
    assert response.status_code == 200
    assert len(response.json()) >= 3
