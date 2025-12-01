from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.faq import FAQ
from app.models.privacy_policy import PrivacyPolicySection
from app.models.why_us import WhyUsStat, WhyUsFeature
from app.schemas.account import (
    ProfileUpdateRequest, TechnicianProfileUpdateRequest,
    PoolOwnerProfileUpdateRequest, CompanyProfileUpdateRequest,
    ProfileResponse, FAQResponse,
    PrivacySectionResponse, WhyUsResponse, WhyUsStatResponse,
    WhyUsFeatureResponse, DeleteAccountConfirm, DeleteAccountResponse
)
from app.models.enums import UserRole

router = APIRouter()

# ============= Profile Information =============

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
    profile_update: TechnicianProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب الفني
    Update technician profile information
    """
    if current_user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للفنيين فقط"
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # معالجة skills - تحويل من list إلى comma-separated string
    if 'skills' in update_data and update_data['skills'] is not None:
        update_data['skills'] = ", ".join(update_data['skills'])
    
    # تحديث الحقول
    for field, value in update_data.items():
        if value is not None:
            setattr(current_user, field, value)
    
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
    profile_update: PoolOwnerProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب صاحب الحمام
    Update pool owner profile information
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص لأصحاب المسابح فقط"
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # تحديث الحقول
    for field, value in update_data.items():
        if value is not None:
            setattr(current_user, field, value)
    
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
    profile_update: CompanyProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    تحديث معلومات حساب الشركة
    Update company profile information
    """
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذا الـ endpoint مخصص للشركات فقط"
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # تحديث الحقول
    for field, value in update_data.items():
        if value is not None:
            setattr(current_user, field, value)
    
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

# ============= Help Center (FAQ) =============

@router.get("/account/help-center", response_model=List[FAQResponse])
async def get_faqs(
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    الحصول على الأسئلة الشائعة
    Get frequently asked questions
    """
    query = db.query(FAQ).filter(FAQ.is_active == True)
    
    if category:
        query = query.filter(FAQ.category == category)
    
    faqs = query.order_by(FAQ.sort_order, FAQ.id).all()
    return faqs

# ============= Privacy and Security =============

@router.get("/account/privacy-security", response_model=List[PrivacySectionResponse])
async def get_privacy_sections(
    db: Session = Depends(get_db)
):
    """
    الحصول على أقسام الخصوصية والأمان
    Get privacy and security sections
    """
    sections = db.query(PrivacyPolicySection).filter(
        PrivacyPolicySection.is_active == True
    ).order_by(PrivacyPolicySection.sort_order, PrivacyPolicySection.id).all()
    
    return sections

# ============= Why Us =============

@router.get("/account/why-us", response_model=WhyUsResponse)
async def get_why_us(
    db: Session = Depends(get_db)
):
    """
    الحصول على معلومات "لماذا نحن"
    Get "Why Us" information
    """
    # جلب الإحصائيات
    stats = db.query(WhyUsStat).all()
    stats_response = [
        WhyUsStatResponse(
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
            icon=feature.icon
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

