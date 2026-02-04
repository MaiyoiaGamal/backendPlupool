# app/schemas/comment.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="نص التعليق")
    rating: int = Field(..., ge=1, le=5, description="التقييم من 1 إلى 5")

class CommentCreate(CommentBase):
    service_id: Optional[int] = Field(None, description="معرف الخدمة (اختياري)")
    booking_id: Optional[int] = Field(None, description="معرف الحجز (اختياري)")

class CommentResponse(CommentBase):
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    service_id: Optional[int] = None
    booking_id: Optional[int] = None
    created_at: datetime
    relative_time: Optional[str] = None  # مثل "منذ ساعتين"

    class Config:
        from_attributes = True

class CommentsListResponse(BaseModel):
    comments: list[CommentResponse]
    total: int
    average_rating: Optional[float] = None
    sort_by: Optional[str] = "all"  # للتوضيح في الـ response