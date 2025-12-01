from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class ProductStatus(str, enum.Enum):
    ACTIVE = "active"           # متاح
    INACTIVE = "inactive"       # غير متاح
    OUT_OF_STOCK = "out_of_stock"  # نفذ من المخزن

class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"   # خصم نسبة مئوية
    FIXED = "fixed"             # خصم ثابت

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    
    # معلومات أساسية
    name_ar = Column(String(300), nullable=False, index=True)
    name_en = Column(String(300), nullable=True)
    description_ar = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    
    # الفئة
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
    
    # السعر
    original_price = Column(Integer, nullable=False)       # السعر الأصلي
    discount_type = Column(SQLEnum(DiscountType), nullable=True)  # نوع الخصم
    discount_value = Column(Float, nullable=True)          # قيمة الخصم
    final_price = Column(Integer, nullable=False)          # السعر النهائي
    
    # الصور
    image_url = Column(String(500), nullable=True)         # الصورة الرئيسية
    images = Column(Text, nullable=True)                   # صور إضافية (JSON array كـ text)
    
    # المخزون والتوصيل
    stock_quantity = Column(Integer, default=0)            # الكمية المتاحة
    delivery_time = Column(String(50), nullable=True)      # وقت التوصيل (مثال: "24 ساعة")
    free_delivery = Column(Boolean, default=False)         # توصيل مجاني؟
    
    # التقييم
    rating = Column(Float, default=0.0)                    # التقييم (من 0 إلى 5)
    reviews_count = Column(Integer, default=0)             # عدد التقييمات
    
    # الحالة
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.ACTIVE)
    is_featured = Column(Boolean, default=False)           # منتج مميز؟
    
    # الترتيب والعرض
    sort_order = Column(Integer, default=0)                # ترتيب العرض
    views_count = Column(Integer, default=0)               # عدد المشاهدات
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product {self.name_ar}>"
    
    def calculate_final_price(self):
        """حساب السعر النهائي بعد الخصم"""
        if not self.discount_type or not self.discount_value:
            return self.original_price
        
        if self.discount_type == DiscountType.PERCENTAGE:
            discount_amount = self.original_price * (self.discount_value / 100)
            return int(self.original_price - discount_amount)
        elif self.discount_type == DiscountType.FIXED:
            return int(self.original_price - self.discount_value)
        
        return self.original_price