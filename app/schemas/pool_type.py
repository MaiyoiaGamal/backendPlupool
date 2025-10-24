from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base Schema
class PoolTypeBase(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=200, description="اسم نوع المسبح")
    name_en: Optional[str] = Field(None, max_length=200)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    length_meters: Optional[float] = Field(None, ge=0, description="الطول بالمتر")
    width_meters: Optional[float] = Field(None, ge=0, description="العرض بالمتر")
    depth_meters: Optional[float] = Field(None, ge=0, description="العمق بالمتر")
    features: Optional[List[str]] = Field(None, description="المميزات")
    suitable_for: Optional[str] = Field(None, description="مناسب لـ")
    base_price: Optional[int] = Field(None, ge=0, description="السعر الأساسي")
    is_active: bool = Field(default=True)

# Create Schema
class PoolTypeCreate(PoolTypeBase):
    pass

# Update Schema
class PoolTypeUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    length_meters: Optional[float] = Field(None, ge=0)
    width_meters: Optional[float] = Field(None, ge=0)
    depth_meters: Optional[float] = Field(None, ge=0)
    features: Optional[List[str]] = None
    suitable_for: Optional[str] = None
    base_price: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

# Response Schema
class PoolTypeResponse(PoolTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True