def calculate_recovery_score(customer: dict, transaction: dict) -> int:
    """Return a 0-100 score for a failed payment's recoverability."""
    score = 0

    success_rate = customer.get("successful_transactions", 0) / max(customer.get("total_transactions", 1), 1)
    score += int(success_rate * 35)

    if transaction.get("failure_reason") == "insufficient_funds":
        score += 20
    elif transaction.get("failure_reason") == "expired_card":
        score += 15
    elif transaction.get("failure_reason") == "bank_timeout":
        score += 12
    elif transaction.get("failure_reason") == "overdue_invoice":
        score -= 15

    if transaction.get("amount", 0) < 20000:
        score += 10
    elif transaction.get("amount", 0) > 100000:
        score -= 10

    retry_count = transaction.get("retry_count", 0)
    if retry_count == 0:
        score += 15
    elif retry_count == 1:
        score += 5
    else:
        score -= 10

    lifetime_value = customer.get("lifetime_value", 0)
    if lifetime_value > 100000:
        score += 10

    recent_activity = customer.get("last_seen_at") is not None
    if recent_activity:
        score += 10

    return max(0, min(100, score))


def recommend_action(customer: dict, transaction: dict) -> str:
    score = calculate_recovery_score(customer, transaction)
    reason = transaction.get("failure_reason")

    if reason == "insufficient_funds" and score >= 70:
        return "retry"
    if reason == "expired_card":
        return "payment_link"
    if reason == "overdue_invoice":
        return "escalate"
    if reason == "bank_timeout" and score >= 60:
        return "retry"
    return "wait"
