# app/models/booking.py
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    service: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "تنظيف"
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)