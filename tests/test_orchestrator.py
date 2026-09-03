from backend.agents.recovery_agent import RecoveryAgent
from backend.services.recovery_service import RecoveryService
from backend.services.razorpay_service import RazorpayService
from backend.services.webhook_service import WebhookService


def test_recovery_agent_decision() -> None:
    customer = {
        "successful_transactions": 11,
        "failed_transactions": 1,
        "total_transactions": 12,
        "lifetime_value": 50000,
        "last_seen_at": "2026-08-20T12:00:00",
    }
    transaction = {
        "id": "TX-1001",
        "amount": 14999,
        "failure_reason": "insufficient_funds",
        "retry_count": 0,
    }

    result = RecoveryAgent().analyze(customer, transaction)
    assert result["score"] >= 70
    assert result["recommended_action"] in {"retry", "payment_link"}


def test_razorpay_service_actions() -> None:
    service = RazorpayService()
    assert service.retry_payment("TX-1")["status"] == "scheduled"
    assert service.send_payment_link("TX-1", 15000)["status"] == "sent"
    assert service.escalate_human("TX-1")["status"] == "escalated"


def test_webhook_service() -> None:
    service = WebhookService()
    success = service.process_event({"event": "payment.captured"})
    failure = service.process_event({"event": "payment.failed"})

    assert success["status"] == "recovered"
    assert failure["status"] == "failed"


def test_recovery_service_process() -> None:
    customer = {
        "successful_transactions": 11,
        "failed_transactions": 1,
        "total_transactions": 12,
        "lifetime_value": 50000,
        "last_seen_at": "2026-08-20T12:00:00",
    }
    transaction = {
        "id": "TX-1001",
        "amount": 14999,
        "failure_reason": "insufficient_funds",
        "retry_count": 0,
    }

    result = RecoveryService().process(customer, transaction)
    assert "transaction_id" in result
    assert "recommended_action" in result
    assert "execution" in result
