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
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True
    
    class Config:
        from_attributes = True

class FAQCreate(BaseModel):
    question_ar: str = Field(..., min_length=1, max_length=500)
    question_en: Optional[str] = Field(None, max_length=500)
    answer_ar: str = Field(..., min_length=1)
    answer_en: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True

class FAQUpdate(BaseModel):
    question_ar: Optional[str] = Field(None, min_length=1, max_length=500)
    question_en: Optional[str] = Field(None, max_length=500)
    answer_ar: Optional[str] = Field(None, min_length=1)
    answer_en: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

# Privacy Policy Schemas
class PrivacySectionResponse(BaseModel):
    id: int
    title_ar: str
    title_en: Optional[str]
    content_ar: str
    content_en: Optional[str]
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True
    
    class Config:
        from_attributes = True

class PrivacySectionCreate(BaseModel):
    title_ar: str = Field(..., min_length=1, max_length=200)
    title_en: Optional[str] = Field(None, max_length=200)
    content_ar: str = Field(..., min_length=1)
    content_en: Optional[str] = None
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True

class PrivacySectionUpdate(BaseModel):
    title_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    title_en: Optional[str] = Field(None, max_length=200)
    content_ar: Optional[str] = Field(None, min_length=1)
    content_en: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

# Why Us Schemas
class WhyUsStatResponse(BaseModel):
    id: int
    stat_type: str
    value: float
    label_ar: str
    label_en: Optional[str]
    icon: Optional[str]
    
    class Config:
        from_attributes = True

class WhyUsStatCreate(BaseModel):
    stat_type: str = Field(..., max_length=50)
    value: float = Field(..., ge=0)
    label_ar: str = Field(..., max_length=100)
    label_en: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)

class WhyUsStatUpdate(BaseModel):
    stat_type: Optional[str] = Field(None, max_length=50)
    value: Optional[float] = Field(None, ge=0)
    label_ar: Optional[str] = Field(None, max_length=100)
    label_en: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)

class WhyUsFeatureResponse(BaseModel):
    id: int
    title_ar: str
    title_en: Optional[str]
    description_ar: str
    description_en: Optional[str]
    icon: Optional[str]
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True
    
    class Config:
        from_attributes = True

class WhyUsFeatureCreate(BaseModel):
    title_ar: str = Field(..., min_length=1, max_length=200)
    title_en: Optional[str] = Field(None, max_length=200)
    description_ar: str = Field(..., min_length=1)
    description_en: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True

class WhyUsFeatureUpdate(BaseModel):
    title_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    title_en: Optional[str] = Field(None, max_length=200)
    description_ar: Optional[str] = Field(None, min_length=1)
    description_en: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class WhyUsResponse(BaseModel):
    stats: List[WhyUsStatResponse]
    features: List[WhyUsFeatureResponse]

# Delete Account
class DeleteAccountConfirm(BaseModel):
    confirm: bool = Field(..., description="تأكيد حذف الحساب")

class DeleteAccountResponse(BaseModel):
    message: str
    success: bool

