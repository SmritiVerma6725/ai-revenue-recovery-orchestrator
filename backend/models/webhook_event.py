from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    id: str
    event: str
    entity: str
    payload: dict[str, Any]
    created_at: datetime
    verified: bool = False

    class Config:
        from_attributes = True
