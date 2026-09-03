from backend.policies.recovery_policy import RecoveryPolicy, evaluate_action
from backend.scoring.recovery_score import calculate_recovery_score, recommend_action


def test_recovery_score_for_reliable_customer() -> None:
    customer = {
        "successful_transactions": 11,
        "failed_transactions": 1,
        "total_transactions": 12,
        "lifetime_value": 50000,
        "last_seen_at": "2026-08-20T12:00:00",
    }
    transaction = {
        "amount": 14999,
        "failure_reason": "insufficient_funds",
        "retry_count": 0,
        "payment_method": "card",
    }

    score = calculate_recovery_score(customer, transaction)
    assert 70 <= score <= 100


def test_recovery_score_for_high_value_overdue_case() -> None:
    customer = {
        "successful_transactions": 3,
        "failed_transactions": 9,
        "total_transactions": 12,
        "lifetime_value": 300000,
        "last_seen_at": "2026-07-01T09:00:00",
    }
    transaction = {
        "amount": 250000,
        "failure_reason": "overdue_invoice",
        "retry_count": 2,
        "payment_method": "netbanking",
    }

    score = calculate_recovery_score(customer, transaction)
    assert score < 60


def test_recommend_action_for_low_funds() -> None:
    customer = {
        "successful_transactions": 10,
        "failed_transactions": 1,
        "total_transactions": 11,
    }
    transaction = {
        "amount": 15000,
        "failure_reason": "insufficient_funds",
        "retry_count": 0,
    }

    action = recommend_action(customer, transaction)
    assert action in {"retry", "payment_link"}


def test_policy_allows_safe_retry() -> None:
    policy = RecoveryPolicy()
    allowed, reason = evaluate_action(policy, "retry", 15000, retry_count=0, message_count=0)
    assert allowed is True
    assert reason == "allowed"


def test_policy_blocks_excessive_retries() -> None:
    policy = RecoveryPolicy()
    allowed, reason = evaluate_action(policy, "retry", 15000, retry_count=2, message_count=0)
    assert allowed is False
    assert "retry limit" in reason.lower()
