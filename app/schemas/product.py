from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductStatus, DiscountType

# Base Schema
class ProductBase(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=300, description="اسم المنتج بالعربي")
    name_en: Optional[str] = Field(None, max_length=300)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    category_id: Optional[int] = None
    original_price: int = Field(..., ge=0, description="السعر الأصلي")
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    images: Optional[str] = None  # JSON array as string
    stock_quantity: int = Field(default=0, ge=0)
    delivery_time: Optional[str] = Field(None, max_length=50)
    free_delivery: bool = Field(default=False)
    rating: float = Field(default=0.0, ge=0, le=5)
    reviews_count: int = Field(default=0, ge=0)
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    is_featured: bool = Field(default=False)
    sort_order: int = Field(default=0)

# Create Schema
class ProductCreate(ProductBase):
    pass

# Update Schema
class ProductUpdate(BaseModel):
    name_ar: Optional[str] = Field(None, min_length=1, max_length=300)
    name_en: Optional[str] = Field(None, max_length=300)
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    category_id: Optional[int] = None
    original_price: Optional[int] = Field(None, ge=0)
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    images: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    delivery_time: Optional[str] = Field(None, max_length=50)
    free_delivery: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviews_count: Optional[int] = Field(None, ge=0)
    status: Optional[ProductStatus] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None

# Response Schema
class ProductResponse(ProductBase):
    id: int
    final_price: int
    views_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response with Category Details
class ProductDetailResponse(ProductResponse):
    category_name: Optional[str] = None