from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class WhyUsStat(Base):
    """إحصائيات صفحة لماذا نحن"""
    __tablename__ = "why_us_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    stat_type = Column(String(50), unique=True, nullable=False)  # rating, experience_years, completed_projects
    value = Column(Float, nullable=False)
    label_ar = Column(String(100), nullable=False)
    label_en = Column(String(100), nullable=True)
    icon = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WhyUsFeature(Base):
    """مميزات صفحة لماذا نحن"""
    __tablename__ = "why_us_features"
    
    id = Column(Integer, primary_key=True, index=True)
    title_ar = Column(String(200), nullable=False)
    title_en = Column(String(200), nullable=True)
    description_ar = Column(Text, nullable=False)
    description_en = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

