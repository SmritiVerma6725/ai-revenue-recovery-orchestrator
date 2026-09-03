from datetime import datetime

from pydantic import BaseModel


class PaymentFailure(BaseModel):
    id: str
    transaction_id: str
    failure_code: str | None = None
    failure_reason: str | None = None
    failed_at: datetime
    retry_count: int = 0
    recoverable: bool = False
    notes: str | None = None

    class Config:
        from_attributes = True
