from fastapi.testclient import TestClient

from backend.main import app
from backend.services import razorpay_service as razorpay_module


client = TestClient(app)


def test_razorpay_webhook_route() -> None:
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_12345",
                    "amount": 14999,
                    "currency": "INR",
                }
            }
        },
    }

    response = client.post("/api/webhooks/razorpay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recovered"
    assert data["event"] == "payment.captured"


def test_razorpay_webhook_failure_event() -> None:
    response = client.post(
        "/api/webhooks/razorpay",
        json={"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_67890"}}}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_razorpay_webhook_rejects_invalid_signature(monkeypatch) -> None:
    monkeypatch.setattr(razorpay_module.settings, "webhook_secret", "webhook-secret")

    response = client.post(
        "/api/webhooks/razorpay",
        json={"event": "payment.captured"},
        headers={"X-Razorpay-Signature": "invalid"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
