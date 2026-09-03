from __future__ import annotations

from backend.agents.recovery_agent import RecoveryAgent
from backend.policies.recovery_policy import RecoveryPolicy, evaluate_action
from backend.services.razorpay_service import RazorpayService
from backend.services.webhook_service import WebhookService


class RecoveryService:
    def __init__(self) -> None:
        self.agent = RecoveryAgent()
        self.policy = RecoveryPolicy()
        self.razorpay = RazorpayService()
        self.webhook = WebhookService()

    def process(self, customer: dict, transaction: dict) -> dict:
        decision = self.agent.analyze(customer, transaction)
        action = decision["recommended_action"]
        allowed, reason = evaluate_action(
            self.policy,
            action,
            transaction.get("amount", 0),
            transaction.get("retry_count", 0),
            0,
        )

        if not allowed:
            result = self.razorpay.escalate_human(transaction.get("id", "unknown"))
            status = "escalated"
        elif action == "retry":
            result = self.razorpay.retry_payment(transaction.get("id", "unknown"))
            status = "pending"
        elif action == "payment_link":
            result = self.razorpay.send_payment_link(transaction.get("id", "unknown"), transaction.get("amount", 0))
            status = "pending"
        elif action == "reminder":
            result = self.razorpay.send_reminder(transaction.get("id", "unknown"))
            status = "pending"
        else:
            result = self.razorpay.escalate_human(transaction.get("id", "unknown"))
            status = "escalated"

        return {
            "transaction_id": transaction.get("id"),
            "score": decision["score"],
            "diagnosis": decision["diagnosis"],
            "recommended_action": action,
            "guardrail_status": reason,
            "allowed": allowed,
            "execution": result,
            "status": status,
        }

    def process_webhook(self, event_payload: dict) -> dict:
        return self.webhook.process_event(event_payload)
