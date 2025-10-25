from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from app.models.service_offer import OfferStatus, DiscountType

# Base Schema
class ServiceOfferBase(BaseModel):
    title_ar: str = Field(..., min_length=1, max_length=300, description="عنوان العرض")
    title_en: Optional[str] = Field(None, max_length=300)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    service_id: int = Field(..., description="معرف الخدمة")
    original_price: int = Field(..., ge=0, description="السعر الأصلي")
    discount_type: DiscountType = Field(..., description="نوع الخصم")
    discount_value: float = Field(..., ge=0, description="قيمة الخصم")
    sessions_count: Optional[int] = Field(None, ge=1, description="عدد الجلسات")
    bonus_sessions: Optional[int] = Field(None, ge=0, description="جلسات مجانية إضافية")
    image_url: Optional[str] = Field(None, max_length=500)
    badge_text: Optional[str] = Field(None, max_length=100, description="نص البادج (مثل: خصم 10%)")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: OfferStatus = Field(default=OfferStatus.ACTIVE)
    is_featured: bool = Field(default=False)
    sort_order: int = Field(default=0)

# Create Schema
class ServiceOfferCreate(ServiceOfferBase):
    pass

# Update Schema
class ServiceOfferUpdate(BaseModel):
    title_ar: Optional[str] = Field(None, min_length=1, max_length=300)
    title_en: Optional[str] = Field(None, max_length=300)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    service_id: Optional[int] = None
    original_price: Optional[int] = Field(None, ge=0)
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = Field(None, ge=0)
    sessions_count: Optional[int] = Field(None, ge=1)
    bonus_sessions: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    badge_text: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[OfferStatus] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None

# Response Schema
class ServiceOfferResponse(ServiceOfferBase):
    id: int
    final_price: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response with Service Details
class ServiceOfferDetailResponse(ServiceOfferResponse):
    service_name: Optional[str] = None