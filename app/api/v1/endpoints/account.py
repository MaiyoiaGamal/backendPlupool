from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.faq import FAQ
from app.models.privacy_policy import PrivacyPolicySection
from app.models.why_us import WhyUsStat, WhyUsFeature
from app.models.booking import Booking, BookingType, BookingStatus
from app.models.maintenance_package import MaintenancePackage
from app.models.service import Service
from app.models.technician_task import TechnicianTask, TechnicianTaskStatus
from datetime import date, datetime, timedelta
from app.schemas.account import (
    ProfileUpdateRequest, TechnicianProfileUpdateRequest,
    PoolOwnerProfileUpdateRequest, CompanyProfileUpdateRequest,
    ProfileResponse, FAQResponse,
    PrivacySectionResponse, WhyUsResponse, WhyUsStatResponse,
    WhyUsFeatureResponse, DeleteAccountConfirm, DeleteAccountResponse,
    AccountMenuResponse, AccountMenuItem,
    TechnicianProfileInfoResponse, PoolOwnerProfileInfoResponse, CompanyProfileInfoResponse,
    ProjectResponse, ProjectsListResponse, PackageResponse, PackagesListResponse,
    PackageRenewalInfoResponse, PackageRenewalRequest, PackageRenewalResponse
)
from app.models.enums import UserRole
from app.services.upload_service import UploadService
from app.core.validators import Validators

router = APIRouter()

# ============= Account Menu (قائمة حسابي) =============

@router.get("/account/menu", response_model=AccountMenuResponse)
async def get_account_menu(
    current_user: User = Depends(get_current_active_user)
):
    """
    الحصول على قائمة حسابي حسب الدور
    Get account menu based on user role
    """
    menu_items = []
    
    if current_user.role == UserRole.TECHNICIAN:
        # الفني: معلومات الحساب، مركز المساعدة، الخصوصية والأمان، لماذا نحن، تسجيل الخروج
        menu_items = [
            AccountMenuItem(id="profile", title="معلومات الحساب", icon="person", route="/account/profile/info"),
            AccountMenuItem(id="help", title="مركز المساعدة", icon="help", route="/account/help-center"),
            AccountMenuItem(id="privacy", title="الخصوصية والأمان", icon="lock", route="/account/privacy-security"),
            AccountMenuItem(id="why_us", title="لماذا نحن", icon="info", route="/account/why-us"),
            AccountMenuItem(id="logout", title="تسجيل الخروج", icon="logout", route="/auth/logout"),
        ]
    elif current_user.role == UserRole.COMPANY:
        # ممثل الشركة: معلومات الحساب، مشاريعي، خدماتي/باقاتي، مركز المساعدة، الخصوصية والأمان، لماذا نحن، تسجيل الخروج
        menu_items = [
            AccountMenuItem(id="profile", title="معلومات الحساب", icon="person", route="/account/profile/info"),
            AccountMenuItem(id="projects", title="مشاريعي", icon="projects", route="/account/projects"),
            AccountMenuItem(id="services", title="خدماتي / باقاتي", icon="services", route="/account/services-packages"),
            AccountMenuItem(id="help", title="مركز المساعدة", icon="help", route="/account/help-center"),
            AccountMenuItem(id="privacy", title="الخصوصية والأمان", icon="lock", route="/account/privacy-security"),
            AccountMenuItem(id="why_us", title="لماذا نحن", icon="info", route="/account/why-us"),
            AccountMenuItem(id="logout", title="تسجيل الخروج", icon="logout", route="/auth/logout"),
        ]
    elif current_user.role == UserRole.POOL_OWNER:
        # صاحب الحمام: معلومات الحساب، باقاتي، مركز المساعدة، الخصوصية والأمان، لماذا نحن، تسجيل الخروج
        menu_items = [
            AccountMenuItem(id="profile", title="معلومات الحساب", icon="person", route="/account/profile/info"),
            AccountMenuItem(id="packages", title="باقاتي", icon="packages", route="/account/packages"),
            AccountMenuItem(id="help", title="مركز المساعدة", icon="help", route="/account/help-center"),
            AccountMenuItem(id="privacy", title="الخصوصية والأمان", icon="lock", route="/account/privacy-security"),
            AccountMenuItem(id="why_us", title="لماذا نحن", icon="info", route="/account/why-us"),
            AccountMenuItem(id="logout", title="تسجيل الخروج", icon="logout", route="/auth/logout"),
        ]
    else:
        # Default menu
        menu_items = [
            AccountMenuItem(id="profile", title="معلومات الحساب", icon="person", route="/account/profile/info"),
            AccountMenuItem(id="help", title="مركز المساعدة", icon="help", route="/account/help-center"),
            AccountMenuItem(id="privacy", title="الخصوصية والأمان", icon="lock", route="/account/privacy-security"),
            AccountMenuItem(id="why_us", title="لماذا نحن", icon="info", route="/account/why-us"),
            AccountMenuItem(id="logout", title="تسجيل الخروج", icon="logout", route="/auth/logout"),
        ]
    
    return AccountMenuResponse(menu_items=menu_items)

# ============= Profile Information (معلومات الحساب) =============

@router.get("/account/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    الحصول على معلومات الحساب (لكل الأدوار)
    Get account information (for all roles)
    """
    # تحويل skills من comma-separated string إلى list
    skills_list = None
    if current_user.skills:
        skills_list = [skill.strip() for skill in current_user.skills.split(",") if skill.strip()]
    
    return ProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        country_code=getattr(current_user, 'country_code', '+20'),
        full_name=current_user.full_name,
        profile_image=current_user.profile_image,
        address=current_user.address,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
        skills=skills_list,
        years_of_experience=current_user.years_of_experience,
        is_phone_verified=current_user.is_phone_verified,
        created_at=current_user.created_at
    )

@router.get("/account/profile/info")
async def get_profile_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    الحصول على معلومات الحساب حسب الدور (معلومات محددة لكل دور)
    Get profile info based on role (specific info for each role)
    """
    if current_user.role == UserRole.TECHNICIAN:
        # الفني: الصورة، الاسم، محل الإقامة، المهارات، عدد سنين الخبرة، رقم الهاتف
        skills_list = None
        if current_user.skills:
            skills_list = [skill.strip() for skill in current_user.skills.split(",") if skill.strip()]
        
        return TechnicianProfileInfoResponse(
            id=current_user.id,
            profile_image=current_user.profile_image,
            full_name=current_user.full_name,
            address=current_user.address,
            skills=skills_list,
            years_of_experience=current_user.years_of_experience,
            phone=current_user.phone,
            country_code=getattr(current_user, 'country_code', '+20')
        )
    elif current_user.role == UserRole.POOL_OWNER:
        # صاحب الحمام: الصورة، الاسم، محل الإقامة، رقم الهاتف
        return PoolOwnerProfileInfoResponse(
            id=current_user.id,
            profile_image=current_user.profile_image,
            full_name=current_user.full_name,
            address=current_user.address,
            phone=current_user.phone,
            country_code=getattr(current_user, 'country_code', '+20')
        )
    elif current_user.role == UserRole.COMPANY:
        # ممثل الشركة: الصورة، الاسم، رقم الهاتف
        return CompanyProfileInfoResponse(
            id=current_user.id,
            profile_image=current_user.profile_image,
            full_name=current_user.full_name,
            phone=current_user.phone,
            country_code=getattr(current_user, 'country_code', '+20')
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="دور المستخدم غير معروف"
        )

# ============= Upload Profile Image =============

@router.post("/account/profile/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    رفع صورة البروفايل
    Upload profile image
    """
    try:
        # حذف الصورة القديمة إذا كانت موجودة
        if current_user.profile_image:
            UploadService.delete_image(current_user.profile_image)
        
        # رفع الصورة الجديدة
        image_url = await UploadService.upload_profile_image(file, current_user.id)
        
        # تحديث profile_image في الداتابيس
        current_user.profile_image = image_url
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "تم رفع الصورة بنجاح",
            "image_url": image_url,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ أثناء رفع الصورة: {str(e)}"
        )

# ============= Technician Profile =============

@router.get("/account/profile/technician", response_model=ProfileResponse)
async def get_technician_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    الحصول على معلومات حساب الفني
    Get technician profile information
    """
    if current_user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للفنيين فقط"
        )
    
    skills_list = None
    if current_user.skills:
        skills_list = [skill.strip() for skill in current_user.skills.split(",") if skill.strip()]
    
    return ProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        country_code=getattr(current_user, 'country_code', '+20'),
        full_name=current_user.full_name,
        profile_image=current_user.profile_image,
        address=current_user.address,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
        skills=skills_list,
        years_of_experience=current_user.years_of_experience,
        is_phone_verified=current_user.is_phone_verified,
        created_at=current_user.created_at
    )

@router.put("/account/profile/technician", response_model=ProfileResponse)
async def update_technician_profile(
    full_name: Optional[str] = Form(None, min_length=3, max_length=50),
    address: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    skills: Optional[str] = Form(None),  # JSON string or comma-separated
    years_of_experience: Optional[int] = Form(None, ge=0, le=50),
    phone: Optional[str] = Form(None),
    country_code: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب الفني (مع رفع صورة اختياري)
    Update technician profile information (with optional image upload)
    """
    if current_user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للفنيين فقط"
        )
    
    # رفع الصورة إذا كانت موجودة
    if profile_image and profile_image.filename:
        try:
            # حذف الصورة القديمة إذا كانت موجودة
            if current_user.profile_image:
                UploadService.delete_image(current_user.profile_image)
            
            profile_image_url = await UploadService.upload_profile_image(profile_image, current_user.id)
            current_user.profile_image = profile_image_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"حدث خطأ أثناء رفع الصورة: {str(e)}"
            )
    
    # تحديث الحقول الأخرى
    if full_name is not None:
        current_user.full_name = full_name
    if address is not None:
        current_user.address = address
    if latitude is not None:
        current_user.latitude = latitude
    if longitude is not None:
        current_user.longitude = longitude
    if years_of_experience is not None:
        current_user.years_of_experience = years_of_experience
    if phone is not None:
        phone_number, country_code_parsed = Validators.parse_phone_number(phone)
        current_user.phone = phone_number
        if country_code:
            current_user.country_code = country_code
        elif country_code_parsed:
            current_user.country_code = country_code_parsed
    elif country_code is not None:
        current_user.country_code = country_code
    
    # معالجة skills
    if skills is not None:
        try:
            import json
            skills_list = json.loads(skills) if skills.startswith('[') else skills.split(',')
            current_user.skills = ", ".join([s.strip() for s in skills_list if s.strip()])
        except:
            current_user.skills = skills
    
    db.commit()
    db.refresh(current_user)
    
    # إرجاع الاستجابة
    skills_list = None
    if current_user.skills:
        skills_list = [skill.strip() for skill in current_user.skills.split(",") if skill.strip()]
    
    return ProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        country_code=getattr(current_user, 'country_code', '+20'),
        full_name=current_user.full_name,
        profile_image=current_user.profile_image,
        address=current_user.address,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
        skills=skills_list,
        years_of_experience=current_user.years_of_experience,
        is_phone_verified=current_user.is_phone_verified,
        created_at=current_user.created_at
    )

# ============= Pool Owner Profile =============

@router.get("/account/profile/pool-owner", response_model=ProfileResponse)
async def get_pool_owner_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    الحصول على معلومات حساب صاحب الحمام
    Get pool owner profile information
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص لأصحاب المسابح فقط"
        )
    
    return ProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        country_code=getattr(current_user, 'country_code', '+20'),
        full_name=current_user.full_name,
        profile_image=current_user.profile_image,
        address=current_user.address,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
        skills=None,  # Pool owners don't have skills
        years_of_experience=None,  # Pool owners don't have years of experience
        is_phone_verified=current_user.is_phone_verified,
        created_at=current_user.created_at
    )

@router.put("/account/profile/pool-owner", response_model=ProfileResponse)
async def update_pool_owner_profile(
    full_name: Optional[str] = Form(None, min_length=3, max_length=50),
    address: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    phone: Optional[str] = Form(None),
    country_code: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب صاحب الحمام (مع رفع صورة اختياري)
    Update pool owner profile information (with optional image upload)
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص لأصحاب المسابح فقط"
        )
    
    # رفع الصورة إذا كانت موجودة
    if profile_image and profile_image.filename:
        try:
            # حذف الصورة القديمة إذا كانت موجودة
            if current_user.profile_image:
                UploadService.delete_image(current_user.profile_image)
            
            profile_image_url = await UploadService.upload_profile_image(profile_image, current_user.id)
            current_user.profile_image = profile_image_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"حدث خطأ أثناء رفع الصورة: {str(e)}"
            )
    
    # تحديث الحقول الأخرى
    if full_name is not None:
        current_user.full_name = full_name
    if address is not None:
        current_user.address = address
    if latitude is not None:
        current_user.latitude = latitude
    if longitude is not None:
        current_user.longitude = longitude
    if phone is not None:
        phone_number, country_code_parsed = Validators.parse_phone_number(phone)
        current_user.phone = phone_number
        if country_code:
            current_user.country_code = country_code
        elif country_code_parsed:
            current_user.country_code = country_code_parsed
    elif country_code is not None:
        current_user.country_code = country_code
    
    db.commit()
    db.refresh(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        country_code=getattr(current_user, 'country_code', '+20'),
        full_name=current_user.full_name,
        profile_image=current_user.profile_image,
        address=current_user.address,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
        skills=None,
        years_of_experience=None,
        is_phone_verified=current_user.is_phone_verified,
        created_at=current_user.created_at
    )

# ============= Company Profile =============

@router.get("/account/profile/company", response_model=ProfileResponse)
async def get_company_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    الحصول على معلومات حساب الشركة
    Get company profile information
    """
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للشركات فقط"
        )
    
    return ProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        country_code=getattr(current_user, 'country_code', '+20'),
        full_name=current_user.full_name,
        profile_image=current_user.profile_image,
        address=current_user.address,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
        skills=None,  # Companies don't have skills
        years_of_experience=None,  # Companies don't have years of experience
        is_phone_verified=current_user.is_phone_verified,
        created_at=current_user.created_at
    )

@router.put("/account/profile/company", response_model=ProfileResponse)
async def update_company_profile(
    full_name: Optional[str] = Form(None, min_length=3, max_length=50),
    phone: Optional[str] = Form(None),
    country_code: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب الشركة (مع رفع صورة اختياري)
    Update company profile information (with optional image upload)
    """
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للشركات فقط"
        )
    
    # رفع الصورة إذا كانت موجودة
    if profile_image and profile_image.filename:
        try:
            # حذف الصورة القديمة إذا كانت موجودة
            if current_user.profile_image:
                UploadService.delete_image(current_user.profile_image)
            
            profile_image_url = await UploadService.upload_profile_image(profile_image, current_user.id)
            current_user.profile_image = profile_image_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"حدث خطأ أثناء رفع الصورة: {str(e)}"
            )
    
    # تحديث الحقول الأخرى
    if full_name is not None:
        current_user.full_name = full_name
    if phone is not None:
        phone_number, country_code_parsed = Validators.parse_phone_number(phone)
        current_user.phone = phone_number
        if country_code:
            current_user.country_code = country_code
        elif country_code_parsed:
            current_user.country_code = country_code_parsed
    elif country_code is not None:
        current_user.country_code = country_code
    
    db.commit()
    db.refresh(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        country_code=getattr(current_user, 'country_code', '+20'),
        full_name=current_user.full_name,
        profile_image=current_user.profile_image,
        address=current_user.address,
        latitude=current_user.latitude,
        longitude=current_user.longitude,
        skills=None,
        years_of_experience=None,
        is_phone_verified=current_user.is_phone_verified,
        created_at=current_user.created_at
    )

# ============= Packages (باقاتي - صاحب الحمام) =============

@router.get("/account/packages", response_model=PackagesListResponse)
async def get_my_packages(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على باقات صاحب الحمام
    مصنفة: قيد التنفيذ، مجدولة، مكتملة
    Get pool owner's maintenance packages (sorted by status)
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص لأصحاب المسابح فقط"
        )
    
    # جلب الحجوزات من نوع باقة صيانة
    package_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.booking_type == BookingType.MAINTENANCE_PACKAGE
    ).order_by(Booking.created_at.desc()).all()
    
    in_progress = []
    scheduled = []
    completed = []
    
    for booking in package_bookings:
        if not booking.package:
            continue
        
        # نوع الباقة
        package_type_map = {
            "monthly": "الباقة الشهرية",
            "quarterly": "باقة (4 شهور)",
            "yearly": "الباقة السنوية"
        }
        package_type_ar = package_type_map.get(booking.package.duration.value, booking.package.duration.value)
        
        # حساب عدد الزيارات المكتملة (من المهام المرتبطة)
        # للتبسيط، سنستخدم حالة الحجز
        completed_visits = 0
        if booking.status == BookingStatus.COMPLETED:
            completed_visits = booking.package.visits_count or 0
        elif booking.status == BookingStatus.IN_PROGRESS:
            # يمكن حسابها من المهام المكتملة
            completed_visits = (booking.package.visits_count or 0) // 2  # افتراضي
        
        visits_count = booking.package.visits_count or 0
        
        # حساب نسبة التقدم
        progress_percentage = None
        if visits_count > 0:
            progress_percentage = (completed_visits / visits_count) * 100
        
        # تاريخ البداية والانتهاء
        start_date = str(booking.booking_date)
        end_date = None
        # تاريخ الانتهاء = تاريخ البداية + مدة الباقة
        duration_days = {
            "monthly": 30,
            "quarterly": 120,
            "yearly": 365
        }
        days = duration_days.get(booking.package.duration.value, 30)
        end_date = str(booking.booking_date + timedelta(days=days))
        
        # الزيارة القادمة
        next_visit = None
        if booking.next_maintenance_date and booking.status in [BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]:
            next_visit = {
                "date": str(booking.next_maintenance_date),
                "time": "09:00",  # افتراضي
                "reminder": True
            }
        elif booking.booking_date >= date.today() and booking.status == BookingStatus.CONFIRMED:
            next_visit = {
                "date": str(booking.booking_date),
                "time": str(booking.booking_time) if booking.booking_time else "09:00",
                "reminder": True
            }
        
        package_data = PackageResponse(
            booking_id=booking.id,
            package_id=booking.package.id,
            package_name=booking.package.name_ar,
            package_type=package_type_ar,
            start_date=start_date,
            end_date=end_date,
            visits_count=visits_count,
            completed_visits=completed_visits,
            status=booking.status.value,
            next_visit=next_visit,
            progress_percentage=progress_percentage
        )
        
        # تصنيف حسب الحالة
        if booking.status == BookingStatus.COMPLETED:
            completed.append(package_data)
        elif booking.status in [BookingStatus.IN_PROGRESS, BookingStatus.CONFIRMED]:
            in_progress.append(package_data)
        else:  # PENDING
            scheduled.append(package_data)
    
    return PackagesListResponse(
        in_progress=in_progress,
        scheduled=scheduled,
        completed=completed
    )

# ============= Projects (مشاريعي - ممثل الشركة) =============

@router.get("/account/projects", response_model=ProjectsListResponse)
async def get_my_projects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على مشاريع ممثل الشركة (حجوزات إنشاء مسابح)
    مصنفة: قيد التنفيذ، مجدولة، مكتملة
    Get company's construction projects (sorted by status)
    """
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للشركات فقط"
        )
    
    # جلب الحجوزات من نوع إنشاء مسبح
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.booking_type == BookingType.CONSTRUCTION
    ).order_by(Booking.created_at.desc()).all()
    
    in_progress = []
    scheduled = []
    completed = []
    
    for booking in bookings:
        # حساب عدد المسابح من المهام المرتبطة (أو نستخدم 1 كافتراضي)
        # يمكن حسابها من technician_tasks المرتبطة بهذا المشروع
        pools_count = 1  # افتراضي - يمكن تحسينه لاحقاً
        
        # حساب الإنجاز من المهام المرتبطة
        # للتبسيط، سنستخدم حالة الحجز
        completion_percentage = 0.0
        if booking.status == BookingStatus.COMPLETED:
            completion_percentage = 100.0
        elif booking.status == BookingStatus.IN_PROGRESS:
            # يمكن حساب الإنجاز من المهام المكتملة
            completion_percentage = 50.0  # افتراضي
        elif booking.status == BookingStatus.CONFIRMED:
            completion_percentage = 25.0  # بدأ المشروع
        elif booking.status == BookingStatus.PENDING:
            completion_percentage = 0.0
        
        # اسم المشروع (من pool_type أو admin_notes)
        project_name = booking.pool_type.name_ar if booking.pool_type else "مشروع جديد"
        if booking.admin_notes:
            # يمكن استخدام admin_notes كاسم المشروع
            project_name = booking.admin_notes.split('\n')[0] if '\n' in booking.admin_notes else booking.admin_notes
        
        # الموقع (من عنوان المستخدم أو booking)
        location = booking.user.address if booking.user else None
        
        # الزيارة القادمة (من next_maintenance_date أو booking_date)
        next_visit = None
        if booking.next_maintenance_date:
            next_visit = {
                "date": str(booking.next_maintenance_date),
                "time": str(booking.booking_time) if booking.booking_time else "09:00",
                "reminder": True
            }
        elif booking.booking_date >= date.today() and booking.status in [BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]:
            next_visit = {
                "date": str(booking.booking_date),
                "time": str(booking.booking_time) if booking.booking_time else "09:00",
                "reminder": True
            }
        
        project_data = ProjectResponse(
            booking_id=booking.id,
            project_name=project_name,
            location=location,
            pools_count=pools_count,
            completion_percentage=completion_percentage,
            status=booking.status.value,
            start_date=str(booking.booking_date) if booking.booking_date else None,
            end_date=str(booking.next_maintenance_date) if booking.next_maintenance_date else None,
            next_visit=next_visit
        )
        
        # تصنيف حسب الحالة
        if booking.status == BookingStatus.COMPLETED:
            completed.append(project_data)
        elif booking.status in [BookingStatus.IN_PROGRESS, BookingStatus.CONFIRMED]:
            in_progress.append(project_data)
        else:  # PENDING, SCHEDULED
            scheduled.append(project_data)
    
    return ProjectsListResponse(
        in_progress=in_progress,
        scheduled=scheduled,
        completed=completed
    )

# ============= Services & Packages (خدماتي/باقاتي - ممثل الشركة) =============

@router.get("/account/services-packages", response_model=PackagesListResponse)
async def get_my_services_packages(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على باقات ممثل الشركة
    مصنفة: قيد التنفيذ، مجدولة، مكتملة
    Get company's maintenance packages (sorted by status)
    """
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للشركات فقط"
        )
    
    # جلب الحجوزات من نوع باقة صيانة
    package_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.booking_type == BookingType.MAINTENANCE_PACKAGE
    ).order_by(Booking.created_at.desc()).all()
    
    in_progress = []
    scheduled = []
    completed = []
    
    for booking in package_bookings:
        if not booking.package:
            continue
        
        # نوع الباقة
        package_type_map = {
            "monthly": "الباقة الشهرية",
            "quarterly": "باقة (4 شهور)",
            "yearly": "الباقة السنوية"
        }
        package_type_ar = package_type_map.get(booking.package.duration.value, booking.package.duration.value)
        
        # حساب عدد الزيارات المكتملة (من المهام المرتبطة)
        # للتبسيط، سنستخدم حالة الحجز
        completed_visits = 0
        if booking.status == BookingStatus.COMPLETED:
            completed_visits = booking.package.visits_count or 0
        elif booking.status == BookingStatus.IN_PROGRESS:
            # يمكن حسابها من المهام المكتملة
            completed_visits = (booking.package.visits_count or 0) // 2  # افتراضي
        
        visits_count = booking.package.visits_count or 0
        
        # حساب نسبة التقدم
        progress_percentage = None
        if visits_count > 0:
            progress_percentage = (completed_visits / visits_count) * 100
        
        # تاريخ البداية والانتهاء
        start_date = str(booking.booking_date)
        end_date = None
        # تاريخ الانتهاء = تاريخ البداية + مدة الباقة
        duration_days = {
            "monthly": 30,
            "quarterly": 120,
            "yearly": 365
        }
        days = duration_days.get(booking.package.duration.value, 30)
        end_date = str(booking.booking_date + timedelta(days=days))
        
        # الزيارة القادمة
        next_visit = None
        if booking.next_maintenance_date and booking.status in [BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]:
            next_visit = {
                "date": str(booking.next_maintenance_date),
                "time": "09:00",  # افتراضي
                "reminder": True
            }
        elif booking.booking_date >= date.today() and booking.status == BookingStatus.CONFIRMED:
            next_visit = {
                "date": str(booking.booking_date),
                "time": str(booking.booking_time) if booking.booking_time else "09:00",
                "reminder": True
            }
        
        package_data = PackageResponse(
            booking_id=booking.id,
            package_id=booking.package.id,
            package_name=booking.package.name_ar,
            package_type=package_type_ar,
            start_date=start_date,
            end_date=end_date,
            visits_count=visits_count,
            completed_visits=completed_visits,
            status=booking.status.value,
            next_visit=next_visit,
            progress_percentage=progress_percentage
        )
        
        # تصنيف حسب الحالة
        if booking.status == BookingStatus.COMPLETED:
            completed.append(package_data)
        elif booking.status in [BookingStatus.IN_PROGRESS, BookingStatus.CONFIRMED]:
            in_progress.append(package_data)
        else:  # PENDING
            scheduled.append(package_data)
    
    return PackagesListResponse(
        in_progress=in_progress,
        scheduled=scheduled,
        completed=completed
    )

# ============= Package Renewal (تجديد الباقة) =============

@router.get("/account/packages/{booking_id}/renewal-info", response_model=PackageRenewalInfoResponse)
async def get_package_renewal_info(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على معلومات تجديد الباقة (للـ popup)
    Get package renewal information for popup
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص لأصحاب المسابح فقط"
        )
    
    # جلب الحجز
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id,
        Booking.booking_type == BookingType.MAINTENANCE_PACKAGE
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الحجز غير موجود"
        )
    
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يمكن تجديد الباقات المكتملة فقط"
        )
    
    if not booking.package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الباقة غير موجودة"
        )
    
    # نوع الباقة
    package_type_map = {
        "monthly": "الباقة الشهرية",
        "quarterly": "باقة (4 شهور)",
        "yearly": "الباقة السنوية"
    }
    package_type_ar = package_type_map.get(booking.package.duration.value, booking.package.duration.value)
    
    # التاريخ الافتراضي (اليوم أو بعد انتهاء الباقة)
    from datetime import timedelta
    duration_days = {
        "monthly": 30,
        "quarterly": 120,
        "yearly": 365
    }
    days = duration_days.get(booking.package.duration.value, 30)
    end_date = booking.booking_date + timedelta(days=days)
    
    # التاريخ الافتراضي للتجديد (بعد انتهاء الباقة أو اليوم إذا انتهت)
    default_date = max(end_date, date.today())
    
    # الوقت الافتراضي (من الحجز السابق أو 09:00)
    default_time = str(booking.booking_time) if booking.booking_time else "09:00"
    
    return PackageRenewalInfoResponse(
        package_id=booking.package.id,
        package_name=booking.package.name_ar,
        package_type=package_type_ar,
        default_date=str(default_date),
        default_time=default_time
    )

@router.post("/account/packages/{booking_id}/renew", response_model=PackageRenewalResponse)
async def renew_package(
    booking_id: int,
    renewal_request: PackageRenewalRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تأكيد تجديد الباقة (إنشاء حجز جديد)
    Confirm package renewal (create new booking)
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص لأصحاب المسابح فقط"
        )
    
    # جلب الحجز القديم
    old_booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id,
        Booking.booking_type == BookingType.MAINTENANCE_PACKAGE
    ).first()
    
    if not old_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الحجز غير موجود"
        )
    
    if old_booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يمكن تجديد الباقات المكتملة فقط"
        )
    
    if not old_booking.package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الباقة غير موجودة"
        )
    
    # التحقق من أن الباقة لا تزال نشطة
    if not old_booking.package.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="الباقة غير متاحة للتجديد"
        )
    
    # تحويل التاريخ والوقت
    try:
        booking_date = datetime.strptime(renewal_request.booking_date, "%Y-%m-%d").date()
        booking_time = datetime.strptime(renewal_request.booking_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="صيغة التاريخ أو الوقت غير صحيحة. استخدم YYYY-MM-DD للتاريخ و HH:MM للوقت"
        )
    
    # التحقق من أن التاريخ في المستقبل
    if booking_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="التاريخ يجب أن يكون في المستقبل"
        )
    
    # حساب موعد الصيانة القادم
    from datetime import timedelta
    duration_days = {
        "monthly": 30,
        "quarterly": 120,
        "yearly": 365
    }
    days = duration_days.get(old_booking.package.duration.value, 30)
    next_maintenance_date = booking_date + timedelta(days=days)
    
    # إنشاء حجز جديد
    new_booking = Booking(
        user_id=current_user.id,
        booking_type=BookingType.MAINTENANCE_PACKAGE,
        package_id=old_booking.package_id,
        booking_date=booking_date,
        booking_time=booking_time,
        status=BookingStatus.PENDING,
        next_maintenance_date=next_maintenance_date
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return PackageRenewalResponse(
        message="تم تجديد الباقة بنجاح",
        booking_id=new_booking.id,
        success=True
    )

# ============= Help Center (FAQ) =============

@router.get("/account/help-center", response_model=List[FAQResponse])
async def get_faqs(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على الأسئلة الشائعة (مفلترة تلقائياً حسب دور المستخدم)
    Get frequently asked questions (automatically filtered by user role)
    
    الأسئلة مختلفة لكل دور:
    - الفني: أسئلة خاصة بالفنيين
    - صاحب الحمام: أسئلة خاصة بأصحاب المسابح
    - ممثل الشركة: أسئلة خاصة بالشركات
    - عامة: أسئلة مشتركة لجميع الأدوار
    """
    query = db.query(FAQ).filter(FAQ.is_active == True)
    
    # فلترة حسب الفئة (إذا تم تحديدها يدوياً)
    if category:
        query = query.filter(FAQ.category == category)
    else:
        # فلترة تلقائية حسب دور المستخدم
        role_category_map = {
            UserRole.TECHNICIAN: "technician",
            UserRole.POOL_OWNER: "pool_owner",
            UserRole.COMPANY: "company",
            UserRole.ADMIN: "admin"
        }
        role_category = role_category_map.get(current_user.role)
        
        if role_category:
            # جلب FAQs الخاصة بالدور + العامة
            # FAQs الخاصة بالدور لها الأولوية
            query = query.filter(
                (FAQ.category == role_category) | (FAQ.category == "general") | (FAQ.category.is_(None))
            )
        else:
            # إذا لم يكن الدور معروف، نرجع فقط العامة
            query = query.filter(
                (FAQ.category == "general") | (FAQ.category.is_(None))
            )
    
    # الترتيب: FAQs الخاصة بالدور أولاً، ثم العامة
    faqs = query.order_by(
        FAQ.category.desc().nullslast(),  # FAQs الخاصة بالدور أولاً
        FAQ.sort_order,
        FAQ.id
    ).all()
    
    return faqs

# ============= Privacy and Security =============

@router.get("/account/privacy-security", response_model=List[PrivacySectionResponse])
async def get_privacy_sections(
    role: Optional[str] = Query(None, description="فلترة حسب الدور"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على أقسام الخصوصية والأمان (مع فلترة حسب الدور)
    Get privacy and security sections (filtered by role)
    """
    query = db.query(PrivacyPolicySection).filter(
        PrivacyPolicySection.is_active == True
    )
    
    # يمكن إضافة فلترة حسب الدور في المستقبل إذا أضفنا category للأقسام
    # حالياً نرجع جميع الأقسام النشطة
    
    sections = query.order_by(PrivacyPolicySection.sort_order, PrivacyPolicySection.id).all()
    
    return sections

# ============= Why Us =============

@router.get("/account/why-us", response_model=WhyUsResponse)
async def get_why_us(
    role: Optional[str] = Query(None, description="فلترة حسب الدور"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على معلومات "لماذا نحن" (يمكن تخصيصها حسب الدور)
    Get "Why Us" information (can be customized by role)
    """
    # جلب الإحصائيات
    stats = db.query(WhyUsStat).all()
    stats_response = [
        WhyUsStatResponse(
            id=stat.id,
            stat_type=stat.stat_type,
            value=stat.value,
            label_ar=stat.label_ar,
            label_en=stat.label_en,
            icon=stat.icon
        ) for stat in stats
    ]
    
    # جلب المميزات
    features = db.query(WhyUsFeature).filter(
        WhyUsFeature.is_active == True
    ).order_by(WhyUsFeature.sort_order, WhyUsFeature.id).all()
    
    features_response = [
        WhyUsFeatureResponse(
            id=feature.id,
            title_ar=feature.title_ar,
            title_en=feature.title_en,
            description_ar=feature.description_ar,
            description_en=feature.description_en,
            icon=feature.icon,
            sort_order=feature.sort_order,
            is_active=feature.is_active
        ) for feature in features
    ]
    
    return WhyUsResponse(
        stats=stats_response,
        features=features_response
    )

# ============= Delete Account =============

@router.post("/account/delete", response_model=DeleteAccountResponse)
async def delete_account(
    confirm: DeleteAccountConfirm,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    حذف الحساب
    Delete account
    """
    if not confirm.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يجب تأكيد حذف الحساب"
        )
    
    # حذف المستخدم (CASCADE سيتولى حذف البيانات المرتبطة)
    db.delete(current_user)
    db.commit()
    
    return DeleteAccountResponse(
        message="تم حذف الحساب بنجاح",
        success=True
    )

