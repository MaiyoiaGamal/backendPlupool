from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole
from app.core.validators import Validators, ValidationError

class UserBase(BaseModel):
    phone: str = Field(..., description="رقم الموبايل")
    full_name: Optional[str] = Field(None, description="الاسم الكامل")
    role: UserRole
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        try:
            return Validators.phone(v)
        except ValidationError as e:
            raise ValueError(str(e))

# Guest browsing (no signup needed)
class GuestRequest(BaseModel):
    role: UserRole = UserRole.GUEST

# Step 1: Send OTP
class SendOTPRequest(BaseModel):
    phone: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        try:
            return Validators.phone(v)
        except ValidationError as e:
            raise ValueError(str(e))

class SendOTPResponse(BaseModel):
    message: str
    phone: str
    expires_in: int  # seconds

# Step 2: Verify OTP (Login)
class VerifyOTPRequest(BaseModel):
    phone: str
    otp_code: str

# Step 3: Complete Profile (Sign Up)
class TechnicianSignUp(BaseModel):
    phone: str
    otp_code: str
    full_name: str = Field(..., min_length=3, max_length=50)
    profile_image: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    skills: List[str]  # ["تنظيف", "صيانة فلاتر", "إصلاح مضخات"]
    years_of_experience: int = Field(..., ge=0, le=50)
    
    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v):
        try:
            return Validators.name(v)
        except ValidationError as e:
            raise ValueError(str(e))

class PoolOwnerSignUp(BaseModel):
    phone: str
    otp_code: str
    full_name: str = Field(..., min_length=3, max_length=50)
    profile_image: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    
    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v):
        try:
            return Validators.name(v)
        except ValidationError as e:
            raise ValueError(str(e))

class CompanySignUp(BaseModel):
    phone: str
    otp_code: str
    full_name: str = Field(..., min_length=3, max_length=50)
    profile_image: Optional[str] = None
    
    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v):
        try:
            return Validators.name(v)
        except ValidationError as e:
            raise ValueError(str(e))

# Response - All fields optional except required ones
class UserResponse(BaseModel):
    id: int
    phone: str
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    role: UserRole
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    skills: Optional[str] = None
    years_of_experience: Optional[int] = None
    is_phone_verified: bool
    is_active: bool
    is_approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    role: UserRole
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    skills: Optional[str] = None
    years_of_experience: Optional[int] = None

    class Config:
        from_attributes = True  # for Pydantic v2 (was orm_mode in v1)