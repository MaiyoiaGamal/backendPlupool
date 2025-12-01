from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question_ar = Column(String(500), nullable=False)
    question_en = Column(String(500), nullable=True)
    answer_ar = Column(Text, nullable=False)
    answer_en = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # general, technical, account, etc.
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FAQ {self.question_ar[:50]}>"

