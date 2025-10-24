from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time, Enum, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from app.models.booking_enums import BookingType, BookingStatus  

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_type = Column(Enum(BookingType), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    # Date & Time
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)

    # Foreign keys (only one will be used based on booking_type)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    pool_type_id = Column(Integer, ForeignKey("pool_types.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("maintenance_packages.id"), nullable=True)

    # Custom pool dimensions (for construction)
    custom_length = Column(Float, nullable=True)
    custom_width = Column(Float, nullable=True)
    custom_depth = Column(Float, nullable=True)

    # Admin fields
    admin_notes = Column(String, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)

    # System fields
    reminder_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    # Relationships (optional but useful for .service, .user, etc.)
    user = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    pool_type = relationship("PoolType", back_populates="bookings")
    package = relationship("MaintenancePackage", back_populates="bookings")