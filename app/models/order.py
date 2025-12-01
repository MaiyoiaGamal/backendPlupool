from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class OrderStatus(str, enum.Enum):
    PENDING = "pending"           # في الانتظار
    CONFIRMED = "confirmed"        # مؤكد
    PROCESSING = "processing"      # قيد المعالجة
    SHIPPED = "shipped"           # تم الشحن
    DELIVERED = "delivered"       # تم التسليم
    CANCELLED = "cancelled"       # ملغي

class PaymentMethod(str, enum.Enum):
    CASH_ON_DELIVERY = "cash_on_delivery"  # الدفع عند الاستلام
    ONLINE = "online"                      # الدفع الإلكتروني

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Order details
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # رقم الطلب
    total_amount = Column(Float, nullable=False)  # الإجمالي
    delivery_fee = Column(Float, default=0.0)     # رسوم التوصيل
    grand_total = Column(Float, nullable=False)  # الإجمالي الكلي
    
    # Delivery info
    delivery_address = Column(Text, nullable=False)
    delivery_phone = Column(String(20), nullable=False)
    
    # Payment
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, default=PaymentMethod.CASH_ON_DELIVERY)
    payment_status = Column(String(20), default="pending")  # pending, paid, failed
    
    # Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"

