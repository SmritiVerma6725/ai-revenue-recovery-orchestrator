from __future__ import annotations

from backend.data.synthetic import build_demo_transactions
from backend.policies.recovery_policy import RecoveryPolicy, evaluate_action
from backend.scoring.recovery_score import calculate_recovery_score, recommend_action

_demo_state = {
    "revenue_at_risk": 2500000,
    "recoverable_amount": 1680000,
    "recovered_amount": 873450,
}


def reset_demo_state() -> None:
    _demo_state.update(
        revenue_at_risk=2500000,
        recoverable_amount=1680000,
        recovered_amount=873450,
    )


def build_demo_dashboard() -> dict:
    recovery_rate = round((_demo_state["recovered_amount"] / _demo_state["recoverable_amount"]) * 100, 1)
    return {
        **_demo_state,
        "recovery_rate": recovery_rate,
        "transactions_analyzed": 10000,
        "recoverable_cases": 2840,
        "failure_reasons": [
            {"label": "Insufficient funds", "value": 34},
            {"label": "Card expired", "value": 22},
            {"label": "Bank timeout", "value": 18},
            {"label": "Subscription failed", "value": 16},
            {"label": "Overdue invoice", "value": 10},
        ],
    }


def build_revenue_trend() -> list[dict]:
    daily_recovered = [24000, 34000, 24000, 34000, 24000, 34000, 24000, 34000, 24000, 34000,
                       24000, 34000, 24000, 34000, 24000, 34000, 24000, 34000, 24000, 34000,
                       24000, 34000, 24000, 34000, 24000, 34000, 24000, 34000, 24000, 37450]
    adjustment = _demo_state["recovered_amount"] - 873450
    cumulative = 0
    trend = []
    for day, amount in enumerate(daily_recovered, start=1):
        if day == len(daily_recovered):
            amount += adjustment
        cumulative += amount
        trend.append({"day": day, "recovered_amount": amount, "cumulative_recovered": cumulative})
    if trend and cumulative != _demo_state["recovered_amount"]:
        trend[-1]["cumulative_recovered"] += _demo_state["recovered_amount"] - cumulative
    return trend


def simulate_recovery(amount: int = 125000) -> dict:
    available_recovery = _demo_state["recoverable_amount"] - _demo_state["recovered_amount"]
    amount = max(1, min(amount, _demo_state["revenue_at_risk"], available_recovery))
    _demo_state["revenue_at_risk"] -= amount
    _demo_state["recovered_amount"] += amount
    return build_demo_dashboard()


def build_recovery_cases() -> list[dict]:
    transactions = build_demo_transactions()
    cases = []
    for item in transactions:
        customer = {
            "successful_transactions": 11,
            "failed_transactions": 1,
            "total_transactions": 12,
            "lifetime_value": 50000,
            "last_seen_at": "2026-08-20T12:00:00",
        }
        score = calculate_recovery_score(customer, item)
        action = recommend_action(customer, item)
        policy = RecoveryPolicy()
        allowed, reason = evaluate_action(policy, action, item["amount"], item["retry_count"], 0)
        cases.append(
            {
                "customer": f"Customer {item['customer_id']}",
                "amount": item["amount"],
                "reason": item["failure_reason"],
                "score": score,
                "action": action,
                "status": "Pending" if allowed else "Escalated",
            }
        )
    return cases


def build_agent_decision() -> dict:
    transaction = build_demo_transactions()[0]
    customer = {
        "successful_transactions": 11,
        "failed_transactions": 1,
        "total_transactions": 12,
        "lifetime_value": 50000,
        "last_seen_at": "2026-08-20T12:00:00",
    }
    score = calculate_recovery_score(customer, transaction)
    action = recommend_action(customer, transaction)
    policy = RecoveryPolicy()
    allowed, reason = evaluate_action(policy, action, transaction["amount"], transaction["retry_count"], 0)

    return {
        "transaction_id": transaction["id"],
        "recovery_probability": score,
        "diagnosis": "Temporary insufficient funds with a strong recent payment history.",
        "decision": "Retry in 24 hours" if allowed else "Escalate to human review",
        "reason": f"Customer has {customer['successful_transactions']} previous successful payments.",
        "guardrail": f"Maximum retries = {policy.max_retries}; status={reason}",
        "status": "pending" if allowed else "escalated",
    }


def build_audit_trail() -> list[dict]:
    return [
        {
            "timestamp": "2026-08-20T09:00:00",
            "event": "payment.failed",
            "agent_reasoning": "High-trust customer with previous successful payments.",
            "action": "Retry scheduled",
            "result": "Retry queued",
        },
        {
            "timestamp": "2026-08-21T09:00:00",
            "event": "retry_failed",
            "agent_reasoning": "Retry did not succeed; temporary issue persisted.",
            "action": "Payment link generated",
            "result": "Link sent to customer",
        },
        {
            "timestamp": "2026-08-21T11:30:00",
            "event": "customer_paid",
            "agent_reasoning": "Customer paid the outstanding amount after the payment link.",
            "action": "Stop all future actions",
            "result": "Recovered and workflow closed",
        },
    ]


def build_recovery_timeline() -> list[dict]:
    return [
        {"step": "Payment failed", "status": "done"},
        {"step": "AI diagnosis", "status": "done"},
        {"step": "Recovery score", "status": "done"},
        {"step": "Retry", "status": "done"},
        {"step": "Retry failed", "status": "done"},
        {"step": "Payment link", "status": "done"},
        {"step": "Customer paid", "status": "done"},
        {"step": "Workflow stopped", "status": "done"},
    ]
