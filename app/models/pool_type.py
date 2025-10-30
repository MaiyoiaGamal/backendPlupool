from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PoolType(Base):
    __tablename__ = "pool_types"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String(200), nullable=False)      # اسم نوع المسبح (مثل: حمام الغطس الصغير)
    name_en = Column(String(200), nullable=True)
    description_ar = Column(Text, nullable=True)        # الوصف
    description_en = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)      # صورة المسبح
    video_url = Column(String(500), nullable=True)      # فيديو توضيحي
    
    # المواصفات
    length_meters = Column(Float, nullable=True)        # الطول بالمتر
    width_meters = Column(Float, nullable=True)         # العرض بالمتر
    depth_meters = Column(Float, nullable=True)         # العمق بالمتر
    
    # المميزات (Features)
    features = Column(JSON, nullable=True)              # مثل: ["تنظيف الشلالات", "خدمة الجاكوزي"]
    
    # الأنشطة المناسبة لها
    suitable_for = Column(Text, nullable=True)          # مناسب لـ: الاستخدام الشخصي البسيط أو أماكن عامة صغيرة
    
    # معلومات الحجز
    base_price = Column(Integer, nullable=True)         # السعر الأساسي
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="pool_type")
    
    def __repr__(self):
        return f"<PoolType {self.name_ar}>"