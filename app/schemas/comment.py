# app/schemas/comment.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    rating: int  # 1-5

class CommentCreate(CommentBase):
    service_id: Optional[int] = None
    booking_id: Optional[int] = None

class CommentResponse(CommentBase):
    id: int
    user_id: int
    created_at: datetime
    user_name: str  # For display on frontend

    class Config:
        from_attributes = True