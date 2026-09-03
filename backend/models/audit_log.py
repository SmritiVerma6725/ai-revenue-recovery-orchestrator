from datetime import datetime

from pydantic import BaseModel


class AuditLog(BaseModel):
    id: str
    recovery_case_id: str
    event: str
    agent_reasoning: str
    action: str
    result: str
    timestamp: datetime

    class Config:
        from_attributes = True
