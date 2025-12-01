from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Profile Update Schema - Technician
class TechnicianProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=50)
    profile_image: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    skills: Optional[List[str]] = None  # List of skills
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    phone: Optional[str] = None
    country_code: Optional[str] = Field(None, description="رمز الدولة مثل +20")

# Profile Update Schema - Pool Owner
class PoolOwnerProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=50)
    profile_image: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    country_code: Optional[str] = Field(None, description="رمز الدولة مثل +20")

# Profile Update Schema - Company
class CompanyProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=50)
    profile_image: Optional[str] = None
    phone: Optional[str] = None
    country_code: Optional[str] = Field(None, description="رمز الدولة مثل +20")

# Generic Profile Update (for backward compatibility)
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=50)
    profile_image: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    skills: Optional[List[str]] = None  # List of skills (Technician only)
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)  # Technician only
    phone: Optional[str] = None
    country_code: Optional[str] = Field(None, description="رمز الدولة مثل +20")

class ProfileResponse(BaseModel):
    id: int
    phone: str
    country_code: Optional[str]
    full_name: Optional[str]
    profile_image: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    skills: Optional[List[str]]  # Convert from comma-separated string
    years_of_experience: Optional[int]
    is_phone_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# FAQ Schemas
class FAQResponse(BaseModel):
    id: int
    question_ar: str
    question_en: Optional[str]
    answer_ar: str
    answer_en: Optional[str]
    category: Optional[str]
    
    class Config:
        from_attributes = True

# Privacy Policy Schemas
class PrivacySectionResponse(BaseModel):
    id: int
    title_ar: str
    title_en: Optional[str]
    content_ar: str
    content_en: Optional[str]
    
    class Config:
        from_attributes = True

# Why Us Schemas
class WhyUsStatResponse(BaseModel):
    stat_type: str
    value: float
    label_ar: str
    label_en: Optional[str]
    icon: Optional[str]
    
    class Config:
        from_attributes = True

class WhyUsFeatureResponse(BaseModel):
    id: int
    title_ar: str
    title_en: Optional[str]
    description_ar: str
    description_en: Optional[str]
    icon: Optional[str]
    
    class Config:
        from_attributes = True

class WhyUsResponse(BaseModel):
    stats: List[WhyUsStatResponse]
    features: List[WhyUsFeatureResponse]

# Delete Account
class DeleteAccountConfirm(BaseModel):
    confirm: bool = Field(..., description="تأكيد حذف الحساب")

class DeleteAccountResponse(BaseModel):
    message: str
    success: bool

