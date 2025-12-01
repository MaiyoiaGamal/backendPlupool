from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, description="الكمية")

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, description="الكمية")

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product_name_ar: str
    product_image_url: Optional[str]
    unit_price: float
    total_price: float  # unit_price * quantity
    created_at: datetime
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_items: int  # عدد المنتجات
    total_amount: float  # الإجمالي
    delivery_fee: float = 0.0
    grand_total: float  # الإجمالي الكلي

