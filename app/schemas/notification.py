# app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}