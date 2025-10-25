from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String(200), nullable=False, unique=True)  # اسم الفئة بالعربي
    name_en = Column(String(200), nullable=True, unique=True)   # اسم الفئة بالإنجليزي
    icon = Column(String(100), nullable=True)                   # أيقونة الفئة
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name_ar}>"