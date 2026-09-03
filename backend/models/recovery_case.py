from datetime import datetime

from pydantic import BaseModel, Field


class RecoveryCase(BaseModel):
    id: str
    transaction_id: str
    customer_id: str
    recovery_score: int = Field(..., ge=0, le=100)
    recoverable_amount: int = 0
    status: str = "open"
    recommended_action: str = "retry"
    created_at: datetime
    closed_at: datetime | None = None
    reasons: list[str] = []

    class Config:
        from_attributes = True
