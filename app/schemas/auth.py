from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.core.validators import Validators, ValidationError

class LogoutResponse(BaseModel):
    message: str
    success: bool
    user_id: Optional[int] = None

class SignUpRequest(BaseModel):
    phone: str = Field(..., description="رقم الموبايل")
    email: Optional[str] = None
    full_name: Optional[str] = Field(None, description="الاسم الكامل")
    password: str = Field(..., description="كلمة المرور")
    confirm_password: str = Field(..., description="تأكيد كلمة المرور")
    role: str = "pool_owner"
    
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
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        try:
            return Validators.password(v, min_length=6, require_number=True)
        except ValidationError as e:
            raise ValueError(str(e))
    
    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v, info):
        password = info.data.get('password')
        try:
            return Validators.confirm_password(v, password)
        except ValidationError as e:
            raise ValueError(str(e))
