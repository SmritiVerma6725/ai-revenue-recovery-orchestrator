from datetime import datetime

from pydantic import BaseModel, Field


class Customer(BaseModel):
    id: str
    name: str
    email: str | None = None
    phone: str | None = None
    customer_since: datetime | None = None
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    lifetime_value: int = 0
    last_seen_at: datetime | None = None

    class Config:
        from_attributes = True
