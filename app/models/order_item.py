from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Product snapshot (in case product details change later)
    product_name_ar = Column(String(300), nullable=False)
    product_image_url = Column(String(500), nullable=True)
    unit_price = Column(Float, nullable=False)  # السعر وقت الشراء
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)  # unit_price * quantity
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OrderItem order_id={self.order_id} product_id={self.product_id} quantity={self.quantity}>"

