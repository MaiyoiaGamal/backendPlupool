from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.service_offer import ServiceOffer, OfferStatus
from app.models.service import Service, ServiceStatus, ServiceType
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.schemas.service_offer import ServiceOfferDetailResponse
from app.core.dependencies import get_current_user

router = APIRouter()

# ============= صفحات الهوم المخصصة =============

@router.get("/pool-owner", summary="الصفحة الرئيسية لصاحب الحمام")
def get_pool_owner_home(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    الصفحة الرئيسية المخصصة لصاحب الحمام
    - حجوزاته القادمة
    - الخدمات المقترحة (صيانة بشكل أساسي)
    - العروض المميزة (مشتركة)
    - إحصائيات شخصية
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذه الصفحة مخصصة لأصحاب المسابح فقط"
        )
    
    today = datetime.now().date()
    
    # الحجوزات القادمة
    upcoming_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.booking_date >= today,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
    ).order_by(Booking.booking_date).limit(5).all()
    
    # الخدمات المقترحة (التركيز على الصيانة)
    suggested_services = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE,
        Service.service_type == ServiceType.MAINTENANCE
    ).order_by(desc(Service.created_at)).limit(4).all()
    
    # العروض المميزة (مشتركة)
    featured_offers = db.query(ServiceOffer).filter(
        ServiceOffer.is_featured == True,
        ServiceOffer.status == OfferStatus.ACTIVE,
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    ).order_by(
        desc(ServiceOffer.sort_order),
        desc(ServiceOffer.created_at)
    ).limit(6).all()
    
    # إحصائيات
    total_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).count()
    
    completed_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.status == BookingStatus.COMPLETED
    ).count()
    
    return {
        "welcome_message": f"مرحباً {current_user.full_name or 'بك'} 🏊",
        "user_type": "pool_owner",
        "stats": {
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "upcoming_bookings": len(upcoming_bookings)
        },
        "upcoming_bookings": upcoming_bookings,
        "suggested_services": suggested_services,
        "featured_offers": featured_offers
    }

@router.get("/company", summary="الصفحة الرئيسية للشركة")
def get_company_home(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    الصفحة الرئيسية المخصصة للشركة
    - الخدمات المتاحة (إنشاء وصيانة)
    - العروض المميزة (مشتركة)
    - إحصائيات عامة
    """
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذه الصفحة مخصصة للشركات فقط"
        )
    
    today = datetime.now().date()
    
    # جميع الخدمات (إنشاء وصيانة)
    construction_services = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE,
        Service.service_type == ServiceType.CONSTRUCTION
    ).order_by(desc(Service.created_at)).limit(5).all()
    
    maintenance_services = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE,
        Service.service_type == ServiceType.MAINTENANCE
    ).order_by(desc(Service.created_at)).limit(5).all()
    
    # العروض المميزة (مشتركة)
    featured_offers = db.query(ServiceOffer).filter(
        ServiceOffer.is_featured == True,
        ServiceOffer.status == OfferStatus.ACTIVE,
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    ).order_by(
        desc(ServiceOffer.sort_order),
        desc(ServiceOffer.created_at)
    ).limit(6).all()
    
    # إحصائيات عامة
    active_services = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE
    ).count()
    
    active_offers = db.query(ServiceOffer).filter(
        ServiceOffer.status == OfferStatus.ACTIVE,
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    ).count()
    
    return {
        "welcome_message": f"مرحباً {current_user.full_name or 'بك'} 🏢",
        "user_type": "company",
        "stats": {
            "active_services": active_services,
            "active_offers": active_offers,
            "construction_services": len(construction_services),
            "maintenance_services": len(maintenance_services)
        },
        "construction_services": construction_services,
        "maintenance_services": maintenance_services,
        "featured_offers": featured_offers
    }

@router.get("/technician", summary="الصفحة الرئيسية للفني")
def get_technician_home(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    الصفحة الرئيسية المخصصة للفني
    - الحجوزات المعينة له (إذا كان هناك نظام تعيين)
    - خدمات الصيانة المتاحة
    - العروض المميزة (مشتركة)
    - إحصائياته
    """
    if current_user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذه الصفحة مخصصة للفنيين فقط"
        )
    
    today = datetime.now().date()
    
    # خدمات الصيانة (مجال عمل الفني)
    maintenance_services = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE,
        Service.service_type == ServiceType.MAINTENANCE
    ).order_by(desc(Service.created_at)).limit(8).all()
    
    # العروض المميزة (مشتركة)
    featured_offers = db.query(ServiceOffer).filter(
        ServiceOffer.is_featured == True,
        ServiceOffer.status == OfferStatus.ACTIVE,
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    ).order_by(
        desc(ServiceOffer.sort_order),
        desc(ServiceOffer.created_at)
    ).limit(6).all()
    
    # إحصائيات الفني
    total_maintenance_services = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE,
        Service.service_type == ServiceType.MAINTENANCE
    ).count()
    
    return {
        "welcome_message": f"مرحباً {current_user.full_name or 'بك'} 🔧",
        "user_type": "technician",
        "profile": {
            "skills": current_user.skills,
            "years_of_experience": current_user.years_of_experience,
            "location": current_user.address
        },
        "stats": {
            "available_maintenance_services": total_maintenance_services,
            "active_offers": len(featured_offers)
        },
        "maintenance_services": maintenance_services,
        "featured_offers": featured_offers
    }

# ============= Endpoints المشتركة =============

@router.get("/featured-offers", response_model=List[ServiceOfferDetailResponse], summary="العروض المميزة (مشتركة)")
def get_featured_offers(
    limit: int = 6,
    db: Session = Depends(get_db)
):
    """
    الحصول على العروض المميزة - مشتركة بين جميع المستخدمين
    - يعرض العروض النشطة فقط
    - مرتبة حسب الأحدث
    """
    today = datetime.now().date()
    
    # الحصول على العروض المميزة والنشطة
    offers = db.query(ServiceOffer).filter(
        ServiceOffer.is_featured == True,
        ServiceOffer.status == OfferStatus.ACTIVE,
        # التحقق من أن العرض لم ينتهي
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    ).order_by(
        desc(ServiceOffer.sort_order),
        desc(ServiceOffer.created_at)
    ).limit(limit).all()
    
    # إضافة تفاصيل الخدمة
    results = []
    for offer in offers:
        offer_dict = ServiceOfferDetailResponse(**offer.__dict__)
        if offer.service:
            offer_dict.service_name = offer.service.name_ar
        results.append(offer_dict)
    
    return results

@router.get("/stats", summary="إحصائيات عامة")
def get_general_stats(db: Session = Depends(get_db)):
    """
    إحصائيات عامة تظهر للجميع
    - عدد العروض النشطة
    - عدد الخدمات المتاحة
    """
    today = datetime.now().date()
    
    active_offers_count = db.query(ServiceOffer).filter(
        ServiceOffer.status == OfferStatus.ACTIVE,
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    ).count()
    
    active_services_count = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE
    ).count()
    
    maintenance_services_count = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE,
        Service.service_type == ServiceType.MAINTENANCE
    ).count()
    
    construction_services_count = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE,
        Service.service_type == ServiceType.CONSTRUCTION
    ).count()
    
    return {
        "active_offers": active_offers_count,
        "active_services": active_services_count,
        "maintenance_services": maintenance_services_count,
        "construction_services": construction_services_count,
        "message": "مرحباً بك في Plupool! 🏊"
    }