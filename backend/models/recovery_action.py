from datetime import datetime

from pydantic import BaseModel


class RecoveryAction(BaseModel):
    id: str
    recovery_case_id: str
    action_type: str
    action_reason: str
    executed_at: datetime
    result: str | None = None
    external_reference: str | None = None
    status: str = "pending"

    class Config:
        from_attributes = True
