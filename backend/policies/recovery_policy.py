class RecoveryPolicy:
    max_retries: int = 2
    max_messages: int = 2
    max_recovery_window_days: int = 7
    high_value_threshold: int = 100000
    min_retry_gap_hours: int = 24


def evaluate_action(policy: RecoveryPolicy, action: str, amount: int, retry_count: int, message_count: int) -> tuple[bool, str]:
    if action == "retry" and retry_count >= policy.max_retries:
        return False, "retry limit reached"

    if action in {"payment_link", "reminder"} and message_count >= policy.max_messages:
        return False, "message limit reached"

    if amount >= policy.high_value_threshold and action in {"retry", "payment_link"}:
        return False, "high-value case needs escalation review"

    return True, "allowed"
