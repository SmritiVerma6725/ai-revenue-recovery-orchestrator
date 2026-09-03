import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "AI Revenue Recovery Orchestrator"
    app_env: str = os.getenv("APP_ENV", "development")
    revenue_at_risk: int = 2500000
    recoverable_amount: int = 1680000
    recovered_amount: int = 873450
    max_retries: int = 2
    max_messages: int = 2
    recovery_window_days: int = 7
    high_value_threshold: int = 100000
    razorpay_key_id: str = os.getenv("RAZORPAY_KEY_ID", "")
    razorpay_key_secret: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "")


settings = Settings()
