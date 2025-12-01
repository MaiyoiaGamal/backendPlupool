from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus, PaymentMethod

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name_ar: str
    product_image_url: Optional[str]
    unit_price: float
    quantity: int
    total_price: float
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    delivery_address: str = Field(..., description="عنوان التوصيل")
    delivery_phone: str = Field(..., description="رقم الهاتف")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH_ON_DELIVERY, description="طريقة الدفع")

class OrderResponse(BaseModel):
    id: int
    order_number: str
    total_amount: float
    delivery_fee: float
    grand_total: float
    delivery_address: str
    delivery_phone: str
    payment_method: PaymentMethod
    payment_status: str
    status: OrderStatus
    created_at: datetime
    delivered_at: Optional[datetime]
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderSummaryResponse(BaseModel):
    order_number: str
    created_at: datetime
    total_amount: float
    delivery_fee: float
    grand_total: float
    status: OrderStatus
    items_count: int
    payment_method: PaymentMethod
    
    class Config:
        from_attributes = True

