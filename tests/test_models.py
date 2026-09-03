from datetime import datetime

from backend.models.audit_log import AuditLog
from backend.models.customer import Customer
from backend.models.payment_failure import PaymentFailure
from backend.models.recovery_action import RecoveryAction
from backend.models.recovery_case import RecoveryCase
from backend.models.transaction import Transaction
from backend.models.webhook_event import WebhookEvent


def test_customer_model() -> None:
    customer = Customer(
        id="CUST-1",
        name="Rahul",
        email="rahul@example.com",
        phone="9999999999",
        customer_since=datetime(2023, 1, 10),
        total_transactions=12,
        successful_transactions=11,
        failed_transactions=1,
        lifetime_value=50000,
    )
    assert customer.id == "CUST-1"
    assert customer.successful_transactions == 11


def test_transaction_model() -> None:
    txn = Transaction(
        id="TX-1",
        customer_id="CUST-1",
        amount=14999,
        currency="INR",
        payment_method="card",
        status="failed",
        created_at=datetime(2026, 8, 20),
        failure_code="BAD_REQUEST_ERROR",
        failure_reason="insufficient_funds",
        retry_count=0,
    )
    assert txn.amount == 14999
    assert txn.failure_reason == "insufficient_funds"


def test_recovery_case_model() -> None:
    case = RecoveryCase(
        id="RC-1",
        transaction_id="TX-1",
        customer_id="CUST-1",
        recovery_score=91,
        recoverable_amount=14999,
        status="open",
        recommended_action="retry",
        created_at=datetime(2026, 8, 20),
        reasons=["low_balance", "historical_success"],
    )
    assert case.recovery_score == 91
    assert "low_balance" in case.reasons


def test_audit_log_and_action_models() -> None:
    action = RecoveryAction(
        id="RA-1",
        recovery_case_id="RC-1",
        action_type="retry",
        action_reason="temporary bank failure",
        executed_at=datetime(2026, 8, 20),
        result="scheduled",
        status="pending",
    )
    audit = AuditLog(
        id="AL-1",
        recovery_case_id="RC-1",
        event="retry_scheduled",
        agent_reasoning="customer is high trust",
        action="retry",
        result="scheduled",
        timestamp=datetime(2026, 8, 20),
    )
    assert action.action_type == "retry"
    assert audit.event == "retry_scheduled"


def test_failure_and_webhook_models() -> None:
    failure = PaymentFailure(
        id="PF-1",
        transaction_id="TX-1",
        failure_code="BAD_REQUEST_ERROR",
        failure_reason="insufficient_funds",
        failed_at=datetime(2026, 8, 20),
        retry_count=0,
        recoverable=True,
    )
    webhook = WebhookEvent(
        id="WH-1",
        event="payment.failed",
        entity="payment",
        payload={"payment": {"id": "TX-1"}},
        created_at=datetime(2026, 8, 20),
        verified=True,
    )
    assert failure.recoverable is True
    assert webhook.event == "payment.failed"
