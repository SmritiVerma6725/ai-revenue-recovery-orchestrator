from __future__ import annotations

from backend.policies.recovery_policy import RecoveryPolicy, evaluate_action
from backend.scoring.recovery_score import calculate_recovery_score, recommend_action


class RecoveryAgent:
    def analyze(self, customer: dict, transaction: dict) -> dict:
        score = calculate_recovery_score(customer, transaction)
        reason = transaction.get("failure_reason", "unknown")
        action = recommend_action(customer, transaction)
        policy = RecoveryPolicy()
        allowed, guardrail_reason = evaluate_action(
            policy,
            action,
            transaction.get("amount", 0),
            transaction.get("retry_count", 0),
            0,
        )

        diagnosis = {
            "insufficient_funds": "Temporary insufficient funds with a strong recent payment history.",
            "expired_card": "The card is expired and the customer must update payment details.",
            "bank_timeout": "The bank gateway timed out, which is usually temporary and recoverable.",
            "overdue_invoice": "The customer has an overdue balance and the case requires escalation review.",
        }.get(reason, "The failure reason is unclear and needs human review.")

        return {
            "score": score,
            "diagnosis": diagnosis,
            "recommended_action": action,
            "allowed": allowed,
            "guardrail_reason": guardrail_reason,
            "policy": {
                "max_retries": policy.max_retries,
                "max_messages": policy.max_messages,
                "high_value_threshold": policy.high_value_threshold,
            },
        }
