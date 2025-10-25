from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class OfferStatus(str, enum.Enum):
    ACTIVE = "active"           # متاح
    INACTIVE = "inactive"       # غير متاح
    EXPIRED = "expired"         # منتهي

class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"   # خصم نسبة مئوية
    FIXED = "fixed"             # خصم ثابت

class ServiceOffer(Base):
    __tablename__ = "service_offers"

    id = Column(Integer, primary_key=True, index=True)
    
    # معلومات العرض
    title_ar = Column(String(300), nullable=False, index=True)  # عنوان العرض (مثل: عرض تنظيف)
    title_en = Column(String(300), nullable=True)
    description_ar = Column(Text, nullable=True)  # وصف العرض (مثل: جلسة تنظيف مجانية عند حجز 3 جلسات)
    description_en = Column(Text, nullable=True)
    
    # الخدمة المرتبطة
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    service = relationship("Service", backref="offers")
    
    # السعر والخصم
    original_price = Column(Integer, nullable=False)       # السعر الأصلي
    discount_type = Column(SQLEnum(DiscountType), nullable=False)  # نوع الخصم
    discount_value = Column(Float, nullable=False)          # قيمة الخصم
    final_price = Column(Integer, nullable=False)          # السعر بعد الخصم
    
    # شروط العرض
    sessions_count = Column(Integer, nullable=True)        # عدد الجلسات (مثل: 3 جلسات)
    bonus_sessions = Column(Integer, nullable=True)        # جلسات إضافية مجانية
    
    # الصورة
    image_url = Column(String(500), nullable=True)         # صورة العرض
    
    # Badge العرض (مثل: خصم 10%)
    badge_text = Column(String(100), nullable=True)        # النص الظاهر على البادج
    
    # مدة العرض
    start_date = Column(Date, nullable=True)               # تاريخ بداية العرض
    end_date = Column(Date, nullable=True)                 # تاريخ نهاية العرض
    
    # الحالة
    status = Column(SQLEnum(OfferStatus), default=OfferStatus.ACTIVE)
    is_featured = Column(Boolean, default=False)           # عرض مميز (يظهر في الصفحة الرئيسية)
    
    # الترتيب
    sort_order = Column(Integer, default=0)                # ترتيب العرض
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ServiceOffer {self.title_ar}>"
    
    def calculate_final_price(self):
        """حساب السعر النهائي بعد الخصم"""
        if self.discount_type == DiscountType.PERCENTAGE:
            discount_amount = self.original_price * (self.discount_value / 100)
            return int(self.original_price - discount_amount)
        elif self.discount_type == DiscountType.FIXED:
            return int(self.original_price - self.discount_value)
        return self.original_price