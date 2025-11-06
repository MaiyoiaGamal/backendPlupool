from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    Enum as SQLAEnum,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class TaskPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"


class TechnicianTaskStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TechnicianTask(Base):
    __tablename__ = "technician_tasks"

    id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time, nullable=True)

    status = Column(
        SQLAEnum(TechnicianTaskStatus, values_callable=lambda x: [e.value for e in x]),
        default=TechnicianTaskStatus.SCHEDULED,
        nullable=False,
    )
    priority = Column(
        SQLAEnum(TaskPriority, values_callable=lambda x: [e.value for e in x]),
        default=TaskPriority.NORMAL,
        nullable=False,
    )

    location_name = Column(String(255), nullable=True)
    location_address = Column(String(255), nullable=True)
    location_latitude = Column(Float, nullable=True)
    location_longitude = Column(Float, nullable=True)

    customer_name = Column(String(255), nullable=True)
    customer_avatar = Column(String(500), nullable=True)
    customer_phone = Column(String(50), nullable=True)

    notes = Column(Text, nullable=True)

    client_rating = Column(Integer, nullable=True)
    client_feedback = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    technician = relationship("User", back_populates="technician_tasks")

    def mark_completed(
        self,
        rating: Optional[int] = None,
        feedback: Optional[str] = None,
        completed_at_value: Optional[datetime] = None,
    ) -> None:
        self.status = TechnicianTaskStatus.COMPLETED
        self.completed_at = completed_at_value or datetime.utcnow()
        if rating is not None:
            self.client_rating = rating
        if feedback is not None:
            self.client_feedback = feedback
