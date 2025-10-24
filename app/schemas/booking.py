from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date, time
from app.models.booking import BookingType, BookingStatus

# Base Schema
class BookingBase(BaseModel):
    booking_type: BookingType = Field(..., description="نوع الحجز")
    booking_date: date = Field(..., description="تاريخ الحجز")
    booking_time: time = Field(..., description="وقت الحجز")
    notes: Optional[str] = Field(None, description="ملاحظات العميل")

# Create Schema
class BookingCreate(BookingBase):
    service_id: Optional[int] = Field(None, description="معرف الخدمة (للصيانة المفردة)")
    pool_type_id: Optional[int] = Field(None, description="معرف نوع المسبح (للإنشاء)")
    package_id: Optional[int] = Field(None, description="معرف الباقة (للباقات)")
    
    # أبعاد المسبح المخصصة (للإنشاء)
    custom_length: Optional[float] = Field(None, ge=1, description="طول حمام السباحة (بالمتر)")
    custom_width: Optional[float] = Field(None, ge=1, description="عرض حمام السباحة (بالمتر)")
    custom_depth: Optional[float] = Field(None, ge=0.5, description="عمق حمام السباحة (بالمتر)")

    @validator('service_id', 'pool_type_id', 'package_id')
    def validate_booking_type_data(cls, v, values):
        """التحقق من أن البيانات المطلوبة موجودة حسب نوع الحجز"""
        if 'booking_type' in values:
            booking_type = values['booking_type']
            if booking_type == BookingType.CONSTRUCTION and not values.get('pool_type_id'):
                raise ValueError('pool_type_id مطلوب لحجز الإنشاء')
            elif booking_type == BookingType.MAINTENANCE_SINGLE and not values.get('service_id'):
                raise ValueError('service_id مطلوب لحجز الصيانة المفردة')
            elif booking_type == BookingType.MAINTENANCE_PACKAGE and not values.get('package_id'):
                raise ValueError('package_id مطلوب لحجز الباقة')
        return v

# Update Schema (للأدمن)
class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = Field(None, description="حالة الحجز")
    admin_notes: Optional[str] = Field(None, description="ملاحظات الأدمن")
    next_maintenance_date: Optional[date] = Field(None, description="موعد الصيانة القادم")

# Response Schema
class BookingResponse(BookingBase):
    id: int
    user_id: int
    service_id: Optional[int] = None
    pool_type_id: Optional[int] = None
    package_id: Optional[int] = None
    custom_length: Optional[float] = None
    custom_width: Optional[float] = None
    custom_depth: Optional[float] = None
    status: BookingStatus
    admin_notes: Optional[str] = None
    next_maintenance_date: Optional[date] = None
    reminder_sent: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response مع التفاصيل الكاملة
class BookingDetailResponse(BookingResponse):
    service_name: Optional[str] = None
    pool_type_name: Optional[str] = None
    package_name: Optional[str] = None
    user_name: Optional[str] = None