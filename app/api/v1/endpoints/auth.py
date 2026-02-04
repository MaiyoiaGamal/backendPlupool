from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Optional, List

from app.core.config import settings
from app.core.security import create_access_token
from app.core.dependencies import get_current_active_user
from app.core.validators import Validators
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    SendOTPRequest, SendOTPResponse, VerifyOTPRequest,
    TechnicianSignUp, PoolOwnerSignUp, CompanySignUp,
    UserResponse, GuestRequest
)
from app.schemas.token import Token
from app.schemas.auth import LogoutResponse
from app.services.otp_service import OTPService
from app.services.upload_service import UploadService

router = APIRouter()

@router.post("/guest", response_model=UserResponse)
async def browse_as_guest(guest_data: GuestRequest, db: Session = Depends(get_db)):
    """
    تصفح كضيف - لا يحتاج تسجيل
    Guest browsing mode - can view but not book/request
    """
    # Create or return guest session (temporary user)
    # In production, you might use session tokens instead
    return {
        "id": 0,
        "phone": "guest",
        "full_name": "ضيف",
        "role": UserRole.GUEST,
        "is_phone_verified": False,
        "is_active": True,
        "is_approved": False,
        "created_at": datetime.utcnow()
    }

@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """
    إرسال رمز التحقق عبر واتساب
    Send OTP code via WhatsApp
    """
    # Generate OTP
    otp_code = OTPService.generate_otp()
    otp_expiry = OTPService.get_expiry_time(minutes=5)
    
    # فصل كود الدولة عن رقم التليفون
    phone_number, country_code = Validators.parse_phone_number(request.phone)
    
    # Check if user exists (login) or new (signup)
    user = db.query(User).filter(User.phone == phone_number).first()
    
    if user:
        # Existing user - update OTP for login
        user.otp_code = otp_code
        user.otp_expires_at = otp_expiry
        # تحديث كود الدولة إذا تغير
        if user.country_code != country_code:
            user.country_code = country_code
    else:
        # New user - create temporary record
        user = User(
            phone=phone_number,  # رقم التليفون بدون كود الدولة
            country_code=country_code,  # كود الدولة منفصل
            role=UserRole.GUEST,  # Will be updated during signup
            otp_code=otp_code,
            otp_expires_at=otp_expiry
        )
        db.add(user)
    
    db.commit()
    
    # Send OTP via WhatsApp (استخدام الرقم الكامل مع كود الدولة للإرسال)
    full_phone = f"{country_code}{phone_number}" if country_code else phone_number
    await OTPService.send_whatsapp_otp(full_phone, otp_code)
    
    return SendOTPResponse(
        message="تم إرسال رمز التحقق عبر واتساب",
        phone=phone_number,  # إرجاع الرقم بدون كود الدولة
        expires_in=300  # 5 minutes
    )

@router.post("/verify-otp", response_model=Token)
async def verify_otp_login(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    تسجيل الدخول - التحقق من رمز OTP
    Login - Verify OTP code
    """
    # فصل كود الدولة عن رقم التليفون
    phone_number, _ = Validators.parse_phone_number(request.phone)
    
    user = db.query(User).filter(User.phone == phone_number).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رقم الموبايل غير مسجل"
        )
    
    # Verify OTP
    if not OTPService.verify_otp(user.otp_code, user.otp_expires_at, request.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )
    
    # Check if user has completed profile
    if user.role == UserRole.GUEST or not user.full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يرجى إكمال التسجيل أولاً"
        )
    
    # Update user
    user.is_phone_verified = True
    user.last_login = datetime.now(timezone.utc)   
    user.otp_code = None  # Clear OTP
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup/technician", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup_technician(
    phone: str = Form(...),
    otp_code: str = Form(...),
    full_name: str = Form(..., min_length=3, max_length=50),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    skills: str = Form(...),  # JSON string or comma-separated
    years_of_experience: int = Form(..., ge=0, le=50),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    تسجيل فني صيانة (مع رفع صورة اختياري)
    Sign up as Technician (with optional image upload)
    """
    # فصل كود الدولة عن رقم التليفون
    phone_number, country_code = Validators.parse_phone_number(phone)
    
    user = db.query(User).filter(User.phone == phone_number).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يرجى إرسال رمز التحقق أولاً"
        )
    
    # Verify OTP
    if not OTPService.verify_otp(user.otp_code, user.otp_expires_at, otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )
    
    # رفع الصورة إذا كانت موجودة
    profile_image_url = None
    if profile_image and profile_image.filename:
        try:
            profile_image_url = await UploadService.upload_profile_image(profile_image, user.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"حدث خطأ أثناء رفع الصورة: {str(e)}"
            )
    
    # معالجة skills - يمكن أن تكون JSON string أو comma-separated
    try:
        import json
        skills_list = json.loads(skills) if skills.startswith('[') else skills.split(',')
        skills_str = ", ".join([s.strip() for s in skills_list if s.strip()])
    except:
        skills_str = skills
    
    # Update user profile
    user.full_name = full_name
    if profile_image_url:
        user.profile_image = profile_image_url
    user.role = UserRole.TECHNICIAN
    user.latitude = latitude
    user.longitude = longitude
    user.address = address
    user.skills = skills_str
    user.years_of_experience = years_of_experience
    user.country_code = country_code
    user.is_phone_verified = True
    user.last_login = datetime.now(timezone.utc)
    user.otp_code = None
    
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
       data={"sub": str(user.id), "role": user.role.value},
       expires_delta=access_token_expires
    )
   
    return {"access_token": access_token, "token_type": "bearer"}
    
   

@router.post("/signup/pool-owner", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup_pool_owner(
    phone: str = Form(...),
    otp_code: str = Form(...),
    full_name: str = Form(..., min_length=3, max_length=50),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    تسجيل صاحب حمام (مع رفع صورة اختياري)
    Sign up as Pool Owner (with optional image upload)
    """
    # فصل كود الدولة عن رقم التليفون
    phone_number, country_code = Validators.parse_phone_number(phone)
    
    user = db.query(User).filter(User.phone == phone_number).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يرجى إرسال رمز التحقق أولاً"
        )
    
    # Verify OTP
    if not OTPService.verify_otp(user.otp_code, user.otp_expires_at, otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )
    
    # رفع الصورة إذا كانت موجودة
    profile_image_url = None
    if profile_image and profile_image.filename:
        try:
            profile_image_url = await UploadService.upload_profile_image(profile_image, user.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"حدث خطأ أثناء رفع الصورة: {str(e)}"
            )
    
    # Update user profile
    user.full_name = full_name
    if profile_image_url:
        user.profile_image = profile_image_url
    user.role = UserRole.POOL_OWNER
    user.latitude = latitude
    user.longitude = longitude
    user.address = address
    user.country_code = country_code
    user.is_phone_verified = True
    user.last_login = datetime.now(timezone.utc)
    user.otp_code = None
    
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup/company", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup_company(
    phone: str = Form(...),
    otp_code: str = Form(...),
    full_name: str = Form(..., min_length=3, max_length=50),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    تسجيل ممثل شركة (مع رفع صورة اختياري)
    Sign up as Company Representative (with optional image upload)
    """
    # فصل كود الدولة عن رقم التليفون
    phone_number, country_code = Validators.parse_phone_number(phone)
    
    user = db.query(User).filter(User.phone == phone_number).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يرجى إرسال رمز التحقق أولاً"
        )
    
    # Verify OTP
    if not OTPService.verify_otp(user.otp_code, user.otp_expires_at, otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )
    
    # رفع الصورة إذا كانت موجودة
    profile_image_url = None
    if profile_image and profile_image.filename:
        try:
            profile_image_url = await UploadService.upload_profile_image(profile_image, user.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"حدث خطأ أثناء رفع الصورة: {str(e)}"
            )
    
    # Update user profile
    user.full_name = full_name
    if profile_image_url:
        user.profile_image = profile_image_url
    user.role = UserRole.COMPANY
    user.country_code = country_code
    user.is_phone_verified = True
    user.last_login = datetime.now(timezone.utc)
    user.otp_code = None
    
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تسجيل الخروج
    Logout - Clear user session
    
    ملاحظة: في نظام JWT بدون blacklist، الـ token يبقى صالح حتى انتهاء صلاحيته.
    يمكن إضافة token blacklist لاحقاً لتعطيل الـ tokens فوراً.
    """
    # يمكن إضافة منطق إضافي هنا مثل:
    # - إضافة token إلى blacklist (إذا أضفنا نظام blacklist)
    # - حذف refresh tokens
    # - تحديث last_logout timestamp
    
    return LogoutResponse(
        message="تم تسجيل الخروج بنجاح",
        success=True,
        user_id=current_user.id
    )
