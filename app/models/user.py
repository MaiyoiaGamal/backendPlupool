from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLAEnum, Float, Text
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    GUEST = "guest"             # ضيف - Browse only
    POOL_OWNER = "pool_owner"   # صاحب حمام
    TECHNICIAN = "technician"   # فني صيانة
    COMPANY = "company"         # شركة

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info (All roles)
    phone = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)  # URL or path
    role = Column(SQLAEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # Location (Owner & Technician)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    
    # Technician Specific
    skills = Column(Text, nullable=True)  # JSON or comma-separated
    years_of_experience = Column(Integer, nullable=True)
    
    # Authentication
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)
    is_phone_verified = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)  # For manual approval if needed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
