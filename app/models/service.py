from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class ServiceType(str, enum.Enum):
    CONSTRUCTION = "construction"  # إنشاء
    MAINTENANCE = "maintenance"    # صيانة

class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String(200), nullable=False)  # اسم الخدمة بالعربي
    name_en = Column(String(200), nullable=True)   # اسم الخدمة بالإنجليزي
    description_ar = Column(Text, nullable=True)    # وصف الخدمة بالعربي
    description_en = Column(Text, nullable=True)    # وصف الخدمة بالإنجليزي
    service_type = Column(SQLEnum(ServiceType), nullable=False)  # نوع الخدمة
    image_url = Column(String(500), nullable=True)  # رابط الصورة
    icon = Column(String(100), nullable=True)       # أيقونة الخدمة
    price = Column(Integer, nullable=True)          # السعر (اختياري)
    status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="service")
    
    def __repr__(self):
        return f"<Service {self.name_ar} ({self.service_type})>"