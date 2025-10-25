from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.models.service_offer import ServiceOffer, OfferStatus
from app.schemas.service_offer import ServiceOfferDetailResponse

router = APIRouter()

@router.get("/featured-offers", response_model=List[ServiceOfferDetailResponse], summary="العروض المميزة للصفحة الرئيسية")
def get_featured_offers(
    limit: int = 6,
    db: Session = Depends(get_db)
):
    """
    الحصول على العروض المميزة للصفحة الرئيسية
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

@router.get("/home-stats", summary="إحصائيات الصفحة الرئيسية")
def get_home_stats(db: Session = Depends(get_db)):
    """
    إحصائيات تظهر في الصفحة الرئيسية:
    - عدد العروض النشطة
    - عدد الخدمات المتاحة
    - إلخ
    """
    from app.models.service import Service, ServiceStatus
    
    today = datetime.now().date()
    
    active_offers_count = db.query(ServiceOffer).filter(
        ServiceOffer.status == OfferStatus.ACTIVE,
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    ).count()
    
    active_services_count = db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE
    ).count()
    
    return {
        "active_offers": active_offers_count,
        "active_services": active_services_count,
        "message": "مرحباً بك في Plupool! 🏊"
    }