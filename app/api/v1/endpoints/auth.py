from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone

from app.core.config import settings
from app.core.security import create_access_token
from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    SendOTPRequest, SendOTPResponse, VerifyOTPRequest,
    TechnicianSignUp, PoolOwnerSignUp, CompanySignUp,
    UserResponse, GuestRequest
)
from app.schemas.token import Token
from app.services.otp_service import OTPService

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
    
    # Check if user exists (login) or new (signup)
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if user:
        # Existing user - update OTP for login
        user.otp_code = otp_code
        user.otp_expires_at = otp_expiry
    else:
        # New user - create temporary record
        user = User(
            phone=request.phone,
            role=UserRole.GUEST,  # Will be updated during signup
            otp_code=otp_code,
            otp_expires_at=otp_expiry
        )
        db.add(user)
    
    db.commit()
    
    # Send OTP via WhatsApp
    await OTPService.send_whatsapp_otp(request.phone, otp_code)
    
    return SendOTPResponse(
        message="تم إرسال رمز التحقق عبر واتساب",
        phone=request.phone,
        expires_in=300  # 5 minutes
    )

@router.post("/verify-otp", response_model=Token)
async def verify_otp_login(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    تسجيل الدخول - التحقق من رمز OTP
    Login - Verify OTP code
    """
    user = db.query(User).filter(User.phone == request.phone).first()
    
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
async def signup_technician(data: TechnicianSignUp, db: Session = Depends(get_db)):
    """
    تسجيل فني صيانة
    Sign up as Technician
    """
    user = db.query(User).filter(User.phone == data.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يرجى إرسال رمز التحقق أولاً"
        )
    
    # Verify OTP
    if not OTPService.verify_otp(user.otp_code, user.otp_expires_at, data.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )
    
    # Update user profile
    user.full_name = data.full_name
    user.profile_image = data.profile_image
    user.role = UserRole.TECHNICIAN
    user.latitude = data.latitude
    user.longitude = data.longitude
    user.address = data.address
    user.skills = ",".join(data.skills)  # Store as comma-separated
    user.years_of_experience = data.years_of_experience
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
async def signup_pool_owner(data: PoolOwnerSignUp, db: Session = Depends(get_db)):
    """
    تسجيل صاحب حمام
    Sign up as Pool Owner
    """
    user = db.query(User).filter(User.phone == data.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يرجى إرسال رمز التحقق أولاً"
        )
    
    # Verify OTP
    if not OTPService.verify_otp(user.otp_code, user.otp_expires_at, data.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )
    
    # Update user profile
    user.full_name = data.full_name
    user.profile_image = data.profile_image
    user.role = UserRole.POOL_OWNER
    user.latitude = data.latitude
    user.longitude = data.longitude
    user.address = data.address
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
async def signup_company(data: CompanySignUp, db: Session = Depends(get_db)):
    """
    تسجيل ممثل شركة
    Sign up as Company Representative
    """
    user = db.query(User).filter(User.phone == data.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="يرجى إرسال رمز التحقق أولاً"
        )
    
    # Verify OTP
    if not OTPService.verify_otp(user.otp_code, user.otp_expires_at, data.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز التحقق غير صحيح أو منتهي الصلاحية"
        )
    
    # Update user profile
    user.full_name = data.full_name
    user.profile_image = data.profile_image
    user.role = UserRole.COMPANY
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

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تسجيل الخروج
    Logout - Clear user session
    """
    # يمكن إضافة منطق إضافي هنا مثل حذف token من blacklist
    # حالياً فقط نعيد رسالة نجاح
    return {
        "message": "تم تسجيل الخروج بنجاح",
        "success": True
    }
