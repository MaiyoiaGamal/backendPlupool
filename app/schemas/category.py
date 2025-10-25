from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Base Schema
class CategoryBase(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=200, description="اسم الفئة بالعربي")
    name_en: Optional[str] = Field(None, max_length=200, description="اسم الفئة بالإنجليزي")
    icon: Optional[str] = Field(None, max_length=100, description="أيقونة الفئة")
    is_active: bool = Field(default=True)

# Create Schema
class CategoryCreate(CategoryBase):
    pass

# Update Schema
class CategoryUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

# Response Schema
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True