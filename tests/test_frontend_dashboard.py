from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root_dashboard_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Revenue Recovery" in response.text
    assert "Revenue at Risk" in response.text


def test_dashboard_route_page() -> None:
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "recovery-cases" in response.text.lower()
