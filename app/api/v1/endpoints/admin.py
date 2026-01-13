from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional
from app.db.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.enums import UserRole
from app.models.faq import FAQ
from app.models.privacy_policy import PrivacyPolicySection
from app.models.why_us import WhyUsStat, WhyUsFeature
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.account import (
    ProfileResponse, FAQResponse, FAQCreate, FAQUpdate,
    PrivacySectionResponse, PrivacySectionCreate, PrivacySectionUpdate,
    WhyUsStatResponse, WhyUsStatCreate, WhyUsStatUpdate,
    WhyUsFeatureResponse, WhyUsFeatureCreate, WhyUsFeatureUpdate,
    TechnicianProfileUpdateRequest, PoolOwnerProfileUpdateRequest, CompanyProfileUpdateRequest
)

router = APIRouter()

# ============= Admin - Users Management =============

@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = Query(None, description="فلترة حسب الدور"),
    is_active: Optional[bool] = Query(None, description="فلترة حسب الحالة"),
    sort_by: Optional[str] = Query("created_at", description="الترتيب حسب: created_at, id, full_name"),
    order: Optional[str] = Query("desc", description="ترتيب: asc أو desc"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع المستخدمين (للأدمن فقط)
    Get all users (Admin only)
    """
    query = db.query(User)
    
    # فلترة حسب الدور
    if role:
        query = query.filter(User.role == role)
    
    # فلترة حسب الحالة
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # الترتيب
    if sort_by == "created_at":
        query = query.order_by(desc(User.created_at) if order == "desc" else asc(User.created_at))
    elif sort_by == "id":
        query = query.order_by(desc(User.id) if order == "desc" else asc(User.id))
    elif sort_by == "full_name":
        query = query.order_by(desc(User.full_name) if order == "desc" else asc(User.full_name))
    else:
        query = query.order_by(desc(User.created_at))
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على بيانات مستخدم محدد (للأدمن فقط)
    Get specific user by ID (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    return user

@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user_by_admin(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث بيانات مستخدم (للأدمن فقط)
    Update user by admin (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # منع تغيير role إلى ADMIN من خلال هذا endpoint
    # الأدمن يتم تعيينه فقط من endpoint مخصص
    update_data = user_update.dict(exclude_unset=True)
    if 'role' in update_data and update_data['role'] == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="لا يمكن تغيير الدور إلى أدمن من خلال هذا الـ endpoint. استخدم /admin/users/{user_id}/set-admin"
        )
    
    # تحديث الحقول
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/admin/users/{user_id}/set-admin", response_model=UserResponse)
async def set_user_as_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تعيين مستخدم كأدمن (للأدمن فقط - من الباك اند فقط)
    Set user as admin (Admin only - Backend only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="المستخدم أدمن بالفعل"
        )
    
    # تعيين كأدمن
    user.role = UserRole.ADMIN
    user.is_active = True
    user.is_approved = True
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/admin/users/{user_id}/remove-admin", response_model=UserResponse)
async def remove_admin_role(
    user_id: int,
    new_role: UserRole = Query(..., description="الدور الجديد للمستخدم"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    إزالة صلاحيات الأدمن من مستخدم (للأدمن فقط)
    Remove admin role from user (Admin only)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكنك إزالة صلاحيات الأدمن من نفسك"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="المستخدم ليس أدمن"
        )
    
    # التحقق من الدور الجديد
    if new_role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يجب اختيار دور آخر غير الأدمن"
        )
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

@router.put("/admin/users/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تفعيل مستخدم (للأدمن فقط)
    Activate user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

@router.put("/admin/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تعطيل مستخدم (للأدمن فقط)
    Deactivate user (Admin only)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكنك تعطيل نفسك"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف مستخدم (للأدمن فقط)
    Delete user (Admin only)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكنك حذف نفسك"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    db.delete(user)
    db.commit()
    return

# ============= Admin - Dashboard =============

@router.get("/admin/dashboard/stats")
async def get_admin_dashboard_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    إحصائيات لوحة تحكم الأدمن
    Admin dashboard statistics
    """
    # عدد المستخدمين حسب الدور
    total_users = db.query(User).count()
    pool_owners = db.query(User).filter(User.role == UserRole.POOL_OWNER).count()
    technicians = db.query(User).filter(User.role == UserRole.TECHNICIAN).count()
    companies = db.query(User).filter(User.role == UserRole.COMPANY).count()
    admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = db.query(User).filter(User.is_active == False).count()
    
    # المستخدمين الجدد (آخر 30 يوم)
    from datetime import datetime, timedelta, timezone
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    new_users = db.query(User).filter(User.created_at >= thirty_days_ago).count()
    
    return {
        "users": {
            "total": total_users,
            "by_role": {
                "pool_owners": pool_owners,
                "technicians": technicians,
                "companies": companies,
                "admins": admins
            },
            "by_status": {
                "active": active_users,
                "inactive": inactive_users
            },
            "new_last_30_days": new_users
        }
    }

# ============= Admin - FAQ Management =============

@router.get("/admin/faqs", response_model=List[FAQResponse])
async def get_all_faqs_admin(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="فلترة حسب الفئة"),
    is_active: Optional[bool] = Query(None, description="فلترة حسب الحالة"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع الأسئلة الشائعة (للأدمن فقط)
    Get all FAQs (Admin only)
    """
    query = db.query(FAQ)
    
    if category:
        query = query.filter(FAQ.category == category)
    
    if is_active is not None:
        query = query.filter(FAQ.is_active == is_active)
    
    faqs = query.order_by(FAQ.sort_order, FAQ.id).offset(skip).limit(limit).all()
    return faqs

@router.post("/admin/faqs", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq: FAQCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    إضافة سؤال شائع جديد (للأدمن فقط)
    Create new FAQ (Admin only)
    """
    new_faq = FAQ(**faq.dict())
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq

@router.put("/admin/faqs/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: int,
    faq_update: FAQUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث سؤال شائع (للأدمن فقط)
    Update FAQ (Admin only)
    """
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="السؤال الشائع غير موجود"
        )
    
    update_data = faq_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)
    
    db.commit()
    db.refresh(faq)
    return faq

@router.delete("/admin/faqs/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف سؤال شائع (للأدمن فقط)
    Delete FAQ (Admin only)
    """
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="السؤال الشائع غير موجود"
        )
    
    db.delete(faq)
    db.commit()
    return

# ============= Admin - Privacy Policy Management =============

@router.get("/admin/privacy-sections", response_model=List[PrivacySectionResponse])
async def get_all_privacy_sections_admin(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="فلترة حسب الحالة"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع أقسام الخصوصية (للأدمن فقط)
    Get all privacy policy sections (Admin only)
    """
    query = db.query(PrivacyPolicySection)
    
    if is_active is not None:
        query = query.filter(PrivacyPolicySection.is_active == is_active)
    
    sections = query.order_by(PrivacyPolicySection.sort_order, PrivacyPolicySection.id).offset(skip).limit(limit).all()
    return sections

@router.post("/admin/privacy-sections", response_model=PrivacySectionResponse, status_code=status.HTTP_201_CREATED)
async def create_privacy_section(
    section: PrivacySectionCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    إضافة قسم خصوصية جديد (للأدمن فقط)
    Create new privacy policy section (Admin only)
    """
    new_section = PrivacyPolicySection(**section.dict())
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return new_section

@router.put("/admin/privacy-sections/{section_id}", response_model=PrivacySectionResponse)
async def update_privacy_section(
    section_id: int,
    section_update: PrivacySectionUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث قسم خصوصية (للأدمن فقط)
    Update privacy policy section (Admin only)
    """
    section = db.query(PrivacyPolicySection).filter(PrivacyPolicySection.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="قسم الخصوصية غير موجود"
        )
    
    update_data = section_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(section, field, value)
    
    db.commit()
    db.refresh(section)
    return section

@router.delete("/admin/privacy-sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_privacy_section(
    section_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف قسم خصوصية (للأدمن فقط)
    Delete privacy policy section (Admin only)
    """
    section = db.query(PrivacyPolicySection).filter(PrivacyPolicySection.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="قسم الخصوصية غير موجود"
        )
    
    db.delete(section)
    db.commit()
    return

# ============= Admin - Why Us Management =============

@router.get("/admin/why-us/stats", response_model=List[WhyUsStatResponse])
async def get_all_why_us_stats_admin(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع الإحصائيات (للأدمن فقط)
    Get all Why Us stats (Admin only)
    """
    stats = db.query(WhyUsStat).all()
    return stats

@router.post("/admin/why-us/stats", response_model=WhyUsStatResponse, status_code=status.HTTP_201_CREATED)
async def create_why_us_stat(
    stat: WhyUsStatCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    إضافة إحصائية جديدة (للأدمن فقط)
    Create new Why Us stat (Admin only)
    """
    # التحقق من عدم وجود stat_type مكرر
    existing = db.query(WhyUsStat).filter(WhyUsStat.stat_type == stat.stat_type).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"الإحصائية بنوع {stat.stat_type} موجودة بالفعل"
        )
    
    new_stat = WhyUsStat(**stat.dict())
    db.add(new_stat)
    db.commit()
    db.refresh(new_stat)
    return new_stat

@router.put("/admin/why-us/stats/{stat_id}", response_model=WhyUsStatResponse)
async def update_why_us_stat(
    stat_id: int,
    stat_update: WhyUsStatUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث إحصائية (للأدمن فقط)
    Update Why Us stat (Admin only)
    """
    stat = db.query(WhyUsStat).filter(WhyUsStat.id == stat_id).first()
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الإحصائية غير موجودة"
        )
    
    update_data = stat_update.dict(exclude_unset=True)
    
    # التحقق من عدم تكرار stat_type إذا تم تغييره
    if 'stat_type' in update_data and update_data['stat_type'] != stat.stat_type:
        existing = db.query(WhyUsStat).filter(
            WhyUsStat.stat_type == update_data['stat_type'],
            WhyUsStat.id != stat_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"الإحصائية بنوع {update_data['stat_type']} موجودة بالفعل"
            )
    
    for field, value in update_data.items():
        setattr(stat, field, value)
    
    db.commit()
    db.refresh(stat)
    return stat

@router.delete("/admin/why-us/stats/{stat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_why_us_stat(
    stat_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف إحصائية (للأدمن فقط)
    Delete Why Us stat (Admin only)
    """
    stat = db.query(WhyUsStat).filter(WhyUsStat.id == stat_id).first()
    if not stat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الإحصائية غير موجودة"
        )
    
    db.delete(stat)
    db.commit()
    return

@router.get("/admin/why-us/features", response_model=List[WhyUsFeatureResponse])
async def get_all_why_us_features_admin(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="فلترة حسب الحالة"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع المميزات (للأدمن فقط)
    Get all Why Us features (Admin only)
    """
    query = db.query(WhyUsFeature)
    
    if is_active is not None:
        query = query.filter(WhyUsFeature.is_active == is_active)
    
    features = query.order_by(WhyUsFeature.sort_order, WhyUsFeature.id).offset(skip).limit(limit).all()
    return features

@router.post("/admin/why-us/features", response_model=WhyUsFeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_why_us_feature(
    feature: WhyUsFeatureCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    إضافة ميزة جديدة (للأدمن فقط)
    Create new Why Us feature (Admin only)
    """
    new_feature = WhyUsFeature(**feature.dict())
    db.add(new_feature)
    db.commit()
    db.refresh(new_feature)
    return new_feature

@router.put("/admin/why-us/features/{feature_id}", response_model=WhyUsFeatureResponse)
async def update_why_us_feature(
    feature_id: int,
    feature_update: WhyUsFeatureUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث ميزة (للأدمن فقط)
    Update Why Us feature (Admin only)
    """
    feature = db.query(WhyUsFeature).filter(WhyUsFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الميزة غير موجودة"
        )
    
    update_data = feature_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feature, field, value)
    
    db.commit()
    db.refresh(feature)
    return feature

@router.delete("/admin/why-us/features/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_why_us_feature(
    feature_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف ميزة (للأدمن فقط)
    Delete Why Us feature (Admin only)
    """
    feature = db.query(WhyUsFeature).filter(WhyUsFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الميزة غير موجودة"
        )
    
    db.delete(feature)
    db.commit()
    return

# ============= Admin - User Profiles Management (التحكم في صفحات الحساب الشخصي) =============

@router.get("/admin/users/{user_id}/profile", response_model=ProfileResponse)
async def get_user_profile_by_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على معلومات حساب مستخدم محدد (للأدمن فقط)
    Get user profile by admin (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # تحويل skills من comma-separated string إلى list
    skills_list = None
    if user.skills:
        skills_list = [skill.strip() for skill in user.skills.split(",") if skill.strip()]
    
    return ProfileResponse(
        id=user.id,
        phone=user.phone,
        country_code=getattr(user, 'country_code', '+20'),
        full_name=user.full_name,
        profile_image=user.profile_image,
        address=user.address,
        latitude=user.latitude,
        longitude=user.longitude,
        skills=skills_list,
        years_of_experience=user.years_of_experience,
        is_phone_verified=user.is_phone_verified,
        created_at=user.created_at
    )

@router.put("/admin/users/{user_id}/profile/technician")
async def update_technician_profile_by_admin(
    user_id: int,
    profile_update: TechnicianProfileUpdateRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب فني (للأدمن فقط)
    Update technician profile by admin (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    if user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="هذا المستخدم ليس فني"
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # معالجة skills (تحويل list إلى string)
    if "skills" in update_data and update_data["skills"] is not None:
        if isinstance(update_data["skills"], list):
            update_data["skills"] = ", ".join(update_data["skills"])
    
    # تحديث الحقول
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # تحويل skills من string إلى list للـ response
    skills_list = None
    if user.skills:
        skills_list = [skill.strip() for skill in user.skills.split(",") if skill.strip()]
    
    return ProfileResponse(
        id=user.id,
        phone=user.phone,
        country_code=getattr(user, 'country_code', '+20'),
        full_name=user.full_name,
        profile_image=user.profile_image,
        address=user.address,
        latitude=user.latitude,
        longitude=user.longitude,
        skills=skills_list,
        years_of_experience=user.years_of_experience,
        is_phone_verified=user.is_phone_verified,
        created_at=user.created_at
    )

@router.put("/admin/users/{user_id}/profile/pool-owner")
async def update_pool_owner_profile_by_admin(
    user_id: int,
    profile_update: PoolOwnerProfileUpdateRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب صاحب حمام (للأدمن فقط)
    Update pool owner profile by admin (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    if user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="هذا المستخدم ليس صاحب حمام"
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # تحديث الحقول
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return ProfileResponse(
        id=user.id,
        phone=user.phone,
        country_code=getattr(user, 'country_code', '+20'),
        full_name=user.full_name,
        profile_image=user.profile_image,
        address=user.address,
        latitude=user.latitude,
        longitude=user.longitude,
        skills=None,
        years_of_experience=None,
        is_phone_verified=user.is_phone_verified,
        created_at=user.created_at
    )

@router.put("/admin/users/{user_id}/profile/company")
async def update_company_profile_by_admin(
    user_id: int,
    profile_update: CompanyProfileUpdateRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب ممثل شركة (للأدمن فقط)
    Update company profile by admin (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    if user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="هذا المستخدم ليس ممثل شركة"
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # تحديث الحقول
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return ProfileResponse(
        id=user.id,
        phone=user.phone,
        country_code=getattr(user, 'country_code', '+20'),
        full_name=user.full_name,
        profile_image=user.profile_image,
        address=user.address,
        latitude=user.latitude,
        longitude=user.longitude,
        skills=None,
        years_of_experience=None,
        is_phone_verified=user.is_phone_verified,
        created_at=user.created_at
    )

# ============= Admin - Packages Management (التحكم في الباقات) =============

@router.get("/admin/packages")
async def get_all_packages_admin(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع الباقات (للأدمن فقط)
    Get all maintenance packages (Admin only)
    """
    from app.models.maintenance_package import MaintenancePackage
    from app.schemas.maintenance_package import MaintenancePackageResponse
    
    query = db.query(MaintenancePackage)
    
    if is_active is not None:
        query = query.filter(MaintenancePackage.is_active == is_active)
    
    packages = query.order_by(MaintenancePackage.created_at.desc()).offset(skip).limit(limit).all()
    return packages

# ============= Admin - Offers Management (التحكم في العروض) =============

@router.get("/admin/offers")
async def get_all_offers_admin(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع العروض (للأدمن فقط)
    Get all service offers (Admin only)
    """
    from app.models.service_offer import ServiceOffer, OfferStatus
    from app.schemas.service_offer import ServiceOfferResponse
    
    query = db.query(ServiceOffer)
    
    if status:
        try:
            offer_status = OfferStatus(status)
            query = query.filter(ServiceOffer.status == offer_status)
        except ValueError:
            pass
    
    offers = query.order_by(ServiceOffer.created_at.desc()).offset(skip).limit(limit).all()
    return offers

# ============= Admin - Products Management (التحكم في المنتجات/الكروت) =============

@router.get("/admin/products")
async def get_all_products_admin(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة جميع المنتجات/الكروت (للأدمن فقط)
    Get all products (Admin only)
    """
    from app.models.product import Product, ProductStatus
    from app.schemas.product import ProductResponse
    
    query = db.query(Product)
    
    if status:
        try:
            product_status = ProductStatus(status)
            query = query.filter(Product.status == product_status)
        except ValueError:
            pass
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return products
