# app/models/comment.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # e.g., 1-5 stars
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)  # Optional: link to a service
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)  # Optional: link to a booking

    # Relationships
    user = relationship("User", back_populates="comments")
    service = relationship("Service", back_populates="comments")
    booking = relationship("Booking", back_populates="comments")