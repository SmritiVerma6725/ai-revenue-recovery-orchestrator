from datetime import datetime

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    id: str
    customer_id: str
    amount: int = Field(..., ge=0)
    currency: str = "INR"
    payment_method: str = "card"
    status: str = "failed"
    created_at: datetime
    failure_code: str | None = None
    failure_reason: str | None = None
    retry_count: int = 0

    class Config:
        from_attributes = True
