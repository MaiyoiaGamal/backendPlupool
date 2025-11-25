from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship
import enum

class PackageDuration(str, enum.Enum):
    MONTHLY = "monthly"          # الباقة الشهرية
    QUARTERLY = "quarterly"      # الباقة (4 شهور)
    YEARLY = "yearly"            # الباقة السنوية

class MaintenancePackage(Base):
    __tablename__ = "maintenance_packages"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String(200), nullable=False)       # اسم الباقة
    name_en = Column(String(200), nullable=True)
    description_ar = Column(Text, nullable=True)         # وصف الباقة
    description_en = Column(Text, nullable=True)
    
    duration = Column(SQLEnum(PackageDuration), nullable=False)  # المدة (شهري/4 شهور/سنوي)
    
    # الخدمات المشمولة
    included_services = Column(JSON, nullable=True)      # مثل: ["تنظيف شامل", "معالجة المياه", "صيانة المعدات"]
    
    price = Column(Integer, nullable=False)              # السعر
    
    # عدد الزيارات
    visits_count = Column(Integer, nullable=True)        # عدد الزيارات خلال الفترة
    
    # التذكيرات
    reminder_days_before = Column(Integer, default=3)    # التذكير قبل الموعد بكام يوم
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
   
    bookings = relationship("Booking", back_populates="package")
 
    def __repr__(self):
        return f"<MaintenancePackage {self.name_ar} - {self.duration}>"