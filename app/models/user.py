from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLAEnum
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    POOL_OWNER = "pool_owner"  # صاحب حمام
    TECHNICIAN = "technician"   # فني صيانة
    COMPANY = "company"         # شركة

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.POOL_OWNER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
