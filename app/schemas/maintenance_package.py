from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.maintenance_package import PackageDuration

# Base Schema
class MaintenancePackageBase(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=200, description="اسم الباقة")
    name_en: Optional[str] = Field(None, max_length=200)
    description_ar: Optional[str] = Field(None, description="وصف الباقة")
    description_en: Optional[str] = None
    duration: PackageDuration = Field(..., description="المدة (شهري/4 شهور/سنوي)")
    included_services: Optional[List[str]] = Field(None, description="الخدمات المشمولة")
    price: int = Field(..., ge=0, description="السعر")
    visits_count: Optional[int] = Field(None, ge=1, description="عدد الزيارات")
    reminder_days_before: int = Field(default=3, ge=1, description="التذكير قبل الموعد بكام يوم")
    is_active: bool = Field(default=True)

# Create Schema
class MaintenancePackageCreate(MaintenancePackageBase):
    pass

# Update Schema
class MaintenancePackageUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    duration: Optional[PackageDuration] = None
    included_services: Optional[List[str]] = None
    price: Optional[int] = Field(None, ge=0)
    visits_count: Optional[int] = Field(None, ge=1)
    reminder_days_before: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None

# Response Schema
class MaintenancePackageResponse(MaintenancePackageBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True