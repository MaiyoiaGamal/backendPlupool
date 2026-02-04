from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.service_offer import ServiceOffer, OfferStatus, DiscountType
from app.models.service import Service
from app.schemas.service_offer import ServiceOfferCreate, ServiceOfferUpdate, ServiceOfferResponse, ServiceOfferDetailResponse
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter()

# ============= Service Offers APIs (عروض الخدمات - الإنشاء والصيانة) =============
# هذه العروض خاصة بخدمات الإنشاء والصيانة فقط
# متاحة لصاحب الحمام وممثل الشركة
# تظهر في الصفحة الرئيسية (Home Page) لصاحب الحمام وممثل الشركة
# للعروض على المنتجات (معدات الصيانة)، استخدم /products

@router.get("/", response_model=List[ServiceOfferDetailResponse], summary="قائمة عروض الخدمات (الإنشاء والصيانة)")
def get_all_offers(
    service_id: Optional[int] = Query(None, description="فلترة حسب الخدمة"),
    status: Optional[OfferStatus] = Query(None, description="فلترة حسب الحالة"),
    is_featured: Optional[bool] = Query(None, description="العروض المميزة فقط"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة بجميع عروض الخدمات (الإنشاء والصيانة) مع الفلترة
    
    ملاحظة: هذه العروض خاصة بخدمات الإنشاء والصيانة فقط.
    للعروض على المنتجات (معدات الصيانة)، استخدم /products
    """
    today = datetime.now().date()
    
    query = db.query(ServiceOffer)
    
    # فلترة حسب الخدمة
    if service_id:
        query = query.filter(ServiceOffer.service_id == service_id)
    
    # فلترة حسب الحالة
    if status:
        query = query.filter(ServiceOffer.status == status)
    
    # فلترة العروض المميزة
    if is_featured is not None:
        query = query.filter(ServiceOffer.is_featured == is_featured)
    
    # استبعاد العروض المنتهية
    query = query.filter(
        (ServiceOffer.end_date == None) | (ServiceOffer.end_date >= today)
    )
    
    # الترتيب
    query = query.order_by(
        desc(ServiceOffer.sort_order),
        desc(ServiceOffer.created_at)
    )
    
    offers = query.offset(skip).limit(limit).all()
    
    # إضافة تفاصيل الخدمة
    results = []
    for offer in offers:
        offer_dict = ServiceOfferDetailResponse(**offer.__dict__)
        if offer.service:
            offer_dict.service_name = offer.service.name_ar
        results.append(offer_dict)
    
    return results

@router.get("/featured", response_model=List[ServiceOfferDetailResponse], summary="عروض الخدمات المميزة (للصفحة الرئيسية)")
def get_featured_service_offers(
    limit: int = Query(6, description="عدد العروض"),
    db: Session = Depends(get_db)
):
    """
    الحصول على عروض الخدمات المميزة (الإنشاء والصيانة)
    
    هذه العروض خاصة بخدمات:
    - إنشاء المسابح
    - صيانة المسابح
    - تركيب أنظمة الترشيح والإضاءة
    - تنظيف الفلاتر
    
    متاحة لـ: صاحب الحمام وممثل الشركة
    تظهر في: الصفحة الرئيسية (Home Page) عند الضغط على "عرض الكل"
    
    ملاحظة: هذه مختلفة عن منتجات المتجر (معدات الصيانة)
    """
    from app.api.v1.endpoints.home import _fetch_featured_service_offers
    return _fetch_featured_service_offers(limit, db)

@router.get("/{offer_id}", response_model=ServiceOfferDetailResponse, summary="تفاصيل عرض خدمة")
def get_offer(offer_id: int, db: Session = Depends(get_db)):
    """الحصول على تفاصيل عرض معين"""
    offer = db.query(ServiceOffer).filter(ServiceOffer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="العرض غير موجود")
    
    # إضافة تفاصيل الخدمة
    offer_dict = ServiceOfferDetailResponse(**offer.__dict__)
    if offer.service:
        offer_dict.service_name = offer.service.name_ar
    
    return offer_dict

@router.post("/", response_model=ServiceOfferResponse, status_code=status.HTTP_201_CREATED, summary="إضافة عرض خدمة (Admin)")
def create_offer(
    offer: ServiceOfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """إضافة عرض جديد (للأدمن فقط)"""
    
    # التحقق من وجود الخدمة
    service = db.query(Service).filter(Service.id == offer.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="الخدمة غير موجودة")
    
    new_offer = ServiceOffer(**offer.dict())
    
    # حساب السعر النهائي
    new_offer.final_price = new_offer.calculate_final_price()
    
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer

@router.put("/{offer_id}", response_model=ServiceOfferResponse, summary="تحديث عرض خدمة (Admin)")
def update_offer(
    offer_id: int,
    offer: ServiceOfferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """تحديث عرض (للأدمن فقط)"""
    db_offer = db.query(ServiceOffer).filter(ServiceOffer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="العرض غير موجود")
    
    update_data = offer.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_offer, field, value)
    
    # إعادة حساب السعر النهائي
    db_offer.final_price = db_offer.calculate_final_price()
    
    db.commit()
    db.refresh(db_offer)
    return db_offer

@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف عرض خدمة (Admin)")
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """حذف عرض (للأدمن فقط)"""
    db_offer = db.query(ServiceOffer).filter(ServiceOffer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="العرض غير موجود")
    
    db.delete(db_offer)
    db.commit()
    return None