class StoppingRules:
    @staticmethod
    def should_stop(event_status: str) -> bool:
        return event_status in {"recovered", "customer_declined", "recovery_window_expired"}

    @staticmethod
    def should_escalate(event_status: str) -> bool:
        return event_status in {"payment_disputed", "retry_limit_reached"}
