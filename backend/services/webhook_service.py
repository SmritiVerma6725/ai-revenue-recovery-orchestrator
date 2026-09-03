from __future__ import annotations


class WebhookService:
    def process_event(self, payload: dict) -> dict:
        event_name = payload.get("event")
        if event_name in {"payment.captured", "payment_link.paid", "subscription.charged"}:
            return {
                "status": "recovered",
                "event": event_name,
                "action": "stop",
                "message": "Payment succeeded and future recovery actions were stopped.",
            }
        if event_name in {"payment.failed", "subscription.cancelled"}:
            return {
                "status": "failed",
                "event": event_name,
                "action": "continue",
                "message": "The payment still failed; the workflow can continue under policy guardrails.",
            }
        return {
            "status": "ignored",
            "event": event_name,
            "action": "ignore",
            "message": "Event was ignored because it did not change recovery state.",
        }
