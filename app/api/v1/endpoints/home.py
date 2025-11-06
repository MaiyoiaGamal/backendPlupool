from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.service_offer import OfferStatus, ServiceOffer
from app.schemas.service_offer import ServiceOfferDetailResponse


def _summary_with_role(base: str, role_label: Optional[str]) -> str:
    return f"{base} - {role_label}" if role_label else base


def _fetch_featured_offers(limit: int, db: Session) -> List[ServiceOfferDetailResponse]:
    today = datetime.now().date()

    offers = (
        db.query(ServiceOffer)
        .filter(
            ServiceOffer.is_featured == True,
            ServiceOffer.status == OfferStatus.ACTIVE,
            (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today),
        )
        .order_by(
            desc(ServiceOffer.sort_order),
            desc(ServiceOffer.created_at),
        )
        .limit(limit)
        .all()
    )

    results: List[ServiceOfferDetailResponse] = []
    for offer in offers:
        offer_dict = ServiceOfferDetailResponse(**offer.__dict__)
        if offer.service:
            offer_dict.service_name = offer.service.name_ar
        results.append(offer_dict)

    return results


def _fetch_home_stats(db: Session):
    from app.models.service import Service, ServiceStatus

    today = datetime.now().date()

    active_offers_count = (
        db.query(ServiceOffer)
        .filter(
            ServiceOffer.status == OfferStatus.ACTIVE,
            (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today),
        )
        .count()
    )

    active_services_count = (
        db.query(Service)
        .filter(Service.status == ServiceStatus.ACTIVE)
        .count()
    )

    return {
        "active_offers": active_offers_count,
        "active_services": active_services_count,
        "message": "مرحباً بك في Plupool! 🏊",
    }


def create_home_router(role_label: Optional[str] = None) -> APIRouter:
    home_router = APIRouter()

    @home_router.get(
        "/featured-offers",
        response_model=List[ServiceOfferDetailResponse],
        summary=_summary_with_role("العروض المميزة للصفحة الرئيسية", role_label),
    )
    def get_featured_offers(
        limit: int = 6,
        db: Session = Depends(get_db),
    ):
        """
        الحصول على العروض المميزة للصفحة الرئيسية
        - يعرض العروض النشطة فقط
        - مرتبة حسب الأحدث
        """
        return _fetch_featured_offers(limit, db)

    @home_router.get(
        "/home-stats",
        summary=_summary_with_role("إحصائيات الصفحة الرئيسية", role_label),
    )
    def get_home_stats(db: Session = Depends(get_db)):
        """
        إحصائيات تظهر في الصفحة الرئيسية:
        - عدد العروض النشطة
        - عدد الخدمات المتاحة
        - إلخ
        """
        return _fetch_home_stats(db)

    return home_router


router = create_home_router()


__all__ = [
    "router",
    "create_home_router",
    "_fetch_featured_offers",
    "_fetch_home_stats",
]