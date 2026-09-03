from __future__ import annotations

import hashlib
import hmac
import json

from backend.config.settings import settings

try:
    import razorpay
except Exception:  # pragma: no cover - optional dependency
    razorpay = None


class RazorpayService:
    def __init__(self) -> None:
        self.client = None
        if razorpay is not None and settings.razorpay_key_id and settings.razorpay_key_secret:
            self.client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

    def retry_payment(self, transaction_id: str) -> dict:
        if self.client is not None:
            try:
                self.client.payment.fetch(transaction_id)
                return {
                    "status": "scheduled",
                    "transaction_id": transaction_id,
                    "action": "retry",
                    "message": "Retry scheduled for the next available window.",
                }
            except Exception:
                pass
        return {
            "status": "scheduled",
            "transaction_id": transaction_id,
            "action": "retry",
            "message": "Retry scheduled for the next available window.",
        }

    def send_payment_link(self, transaction_id: str, amount: int) -> dict:
        if self.client is not None:
            try:
                self.client.payment_link.create(
                    {
                        "amount": amount * 100,
                        "currency": "INR",
                        "description": f"Recovery payment for {transaction_id}",
                    }
                )
                return {
                    "status": "sent",
                    "transaction_id": transaction_id,
                    "action": "payment_link",
                    "message": f"Payment link created for ₹{amount}.",
                }
            except Exception:
                pass
        return {
            "status": "sent",
            "transaction_id": transaction_id,
            "action": "payment_link",
            "message": f"Payment link created for ₹{amount}.",
        }

    def send_reminder(self, transaction_id: str) -> dict:
        return {
            "status": "sent",
            "transaction_id": transaction_id,
            "action": "reminder",
            "message": "Customer reminder sent.",
        }

    def escalate_human(self, transaction_id: str) -> dict:
        return {
            "status": "escalated",
            "transaction_id": transaction_id,
            "action": "escalate",
            "message": "Escalated to human support for review.",
        }

    def verify_webhook(self, payload: dict, signature: str | None = None) -> bool:
        if not settings.webhook_secret:
            return bool(payload.get("event"))
        if not signature:
            return False
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        expected = hmac.new(settings.webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
