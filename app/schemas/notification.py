# app/schemas/notification.py
from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.technician_task import TaskPriority, TechnicianTaskStatus
from app.schemas.service_offer import ServiceOfferDetailResponse


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TechnicianUpcomingVisit(BaseModel):
    task_id: int
    title: str
    scheduled_date: date
    scheduled_time: Optional[time] = None
    status: TechnicianTaskStatus
    priority: TaskPriority
    customer_name: Optional[str] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    map_url: Optional[str] = None
    relative_time: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TechnicianNotificationsFeedResponse(BaseModel):
    total_upcoming: int
    upcoming_visits: List[TechnicianUpcomingVisit]
    store_offers: List[ServiceOfferDetailResponse]
    last_refreshed_at: datetime
