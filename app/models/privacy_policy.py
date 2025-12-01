from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class PrivacyPolicySection(Base):
    __tablename__ = "privacy_policy_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    title_ar = Column(String(200), nullable=False)
    title_en = Column(String(200), nullable=True)
    content_ar = Column(Text, nullable=False)
    content_en = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PrivacyPolicySection {self.title_ar}>"

