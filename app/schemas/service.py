from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.service import ServiceType, ServiceStatus

# Base Schema
class ServiceBase(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=200, description="اسم الخدمة بالعربي")
    name_en: Optional[str] = Field(None, max_length=200, description="اسم الخدمة بالإنجليزي")
    description_ar: Optional[str] = Field(None, description="وصف الخدمة بالعربي")
    description_en: Optional[str] = Field(None, description="وصف الخدمة بالإنجليزي")
    service_type: ServiceType = Field(..., description="نوع الخدمة (إنشاء أو صيانة)")
    image_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    price: Optional[int] = Field(None, ge=0, description="السعر")
    status: ServiceStatus = Field(default=ServiceStatus.ACTIVE)

# Create Schema
class ServiceCreate(ServiceBase):
    pass

# Update Schema
class ServiceUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    service_type: Optional[ServiceType] = None
    image_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    price: Optional[int] = Field(None, ge=0)
    status: Optional[ServiceStatus] = None

# Response Schema
class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True