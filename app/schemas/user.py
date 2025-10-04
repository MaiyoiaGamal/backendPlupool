from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole
from app.core.validators import Validators, ValidationError

class UserBase(BaseModel):
    phone: str = Field(..., description="رقم الموبايل")
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, description="الاسم الكامل")
    role: UserRole = UserRole.POOL_OWNER
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        try:
            return Validators.phone(v)
        except ValidationError as e:
            raise ValueError(str(e))
    
    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        try:
            return Validators.name(v)
        except ValidationError as e:
            raise ValueError(str(e))

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="كلمة المرور")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        try:
            return Validators.password(v, min_length=6, require_number=True, require_upper=False)
        except ValidationError as e:
            raise ValueError(str(e))

class UserLogin(BaseModel):
    phone: str = Field(..., description="رقم الموبايل")
    password: str = Field(..., description="كلمة المرور")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        try:
            return Validators.phone(v)
        except ValidationError as e:
            raise ValueError(str(e))

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    
    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        try:
            return Validators.name(v)
        except ValidationError as e:
            raise ValueError(str(e))

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    hashed_password: str
