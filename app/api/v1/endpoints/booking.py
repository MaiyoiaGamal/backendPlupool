from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.booking import Booking, BookingType, BookingStatus
from app.models.service import Service
from app.models.pool_type import PoolType
from app.models.maintenance_package import MaintenancePackage
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse, BookingDetailResponse
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter()

# ============= User Bookings APIs =============

@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, summary="إنشاء حجز جديد")
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    إنشاء حجز جديد (للمستخدم)
    - حجز إنشاء مسبح
    - حجز صيانة مرة واحدة
    - حجز باقة صيانة
    """
    
    # التحقق من وجود الخدمة/المسبح/الباقة
    if booking.booking_type == BookingType.CONSTRUCTION:
        pool_type = db.query(PoolType).filter(PoolType.id == booking.pool_type_id).first()
        if not pool_type or not pool_type.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="نوع المسبح غير موجود أو غير متاح"
            )
    
    elif booking.booking_type == BookingType.MAINTENANCE_SINGLE:
        service = db.query(Service).filter(Service.id == booking.service_id).first()
        if not service or service.status != "active":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="الخدمة غير موجودة أو غير متاحة"
            )
    
    elif booking.booking_type == BookingType.MAINTENANCE_PACKAGE:
        package = db.query(MaintenancePackage).filter(MaintenancePackage.id == booking.package_id).first()
        if not package or not package.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="الباقة غير موجودة أو غير متاحة"
            )
        
        # حساب موعد الصيانة القادم للباقات
        next_maintenance_date = booking.booking_date + timedelta(days=30)  # مثال: بعد شهر
    
    # إنشاء الحجز
    new_booking = Booking(
        user_id=current_user.id,
        **booking.dict(),
        next_maintenance_date=next_maintenance_date if booking.booking_type == BookingType.MAINTENANCE_PACKAGE else None
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    # TODO: إرسال إشعار للأدمن بالحجز الجديد
    
    return new_booking

@router.get("/bookings/my-bookings", response_model=List[BookingResponse], summary="حجوزاتي")
def get_my_bookings(
    booking_type: Optional[BookingType] = Query(None, description="فلترة حسب نوع الحجز"),
    status_filter: Optional[BookingStatus] = Query(None, description="فلترة حسب الحالة"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على قائمة حجوزات المستخدم الحالي"""
    query = db.query(Booking).filter(Booking.user_id == current_user.id)
    
    if booking_type:
        query = query.filter(Booking.booking_type == booking_type)
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    bookings = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    return bookings

@router.get("/bookings/my-bookings/{booking_id}", response_model=BookingDetailResponse, summary="تفاصيل حجزي")
def get_my_booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على تفاصيل حجز معين للمستخدم"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الحجز غير موجود"
        )
    
    # إضافة التفاصيل الإضافية
    response = BookingDetailResponse(**booking.__dict__)
    
    if booking.service:
        response.service_name = booking.service.name_ar
    if booking.pool_type:
        response.pool_type_name = booking.pool_type.name_ar
    if booking.package:
        response.package_name = booking.package.name_ar
    
    return response

@router.get("/bookings/my-reminders", response_model=List[BookingResponse], summary="تذكيرات الصيانة")
def get_my_maintenance_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على قائمة بمواعيد الصيانة القادمة (للباقات فقط)"""
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.booking_type == BookingType.MAINTENANCE_PACKAGE,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
        Booking.next_maintenance_date.isnot(None),
        Booking.next_maintenance_date <= next_week
    ).order_by(Booking.next_maintenance_date).all()
    
    return bookings

# ============= Admin Bookings APIs =============

@router.get("/admin/bookings", response_model=List[BookingDetailResponse], summary="جميع الحجوزات (أدمن)")
def get_all_bookings_admin(
    booking_type: Optional[BookingType] = Query(None, description="فلترة حسب نوع الحجز"),
    status_filter: Optional[BookingStatus] = Query(None, description="فلترة حسب الحالة"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """الحصول على قائمة بجميع الحجوزات (للأدمن فقط)"""
    
    query = db.query(Booking)
    
    if booking_type:
        query = query.filter(Booking.booking_type == booking_type)
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    bookings = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    
    # إضافة التفاصيل
    results = []
    for booking in bookings:
        response = BookingDetailResponse(**booking.__dict__)
        
        if booking.service:
            response.service_name = booking.service.name_ar
        if booking.pool_type:
            response.pool_type_name = booking.pool_type.name_ar
        if booking.package:
            response.package_name = booking.package.name_ar
        if booking.user:
            response.user_name = booking.user.full_name
        
        results.append(response)
    
    return results

@router.get("/admin/bookings/pending", response_model=List[BookingDetailResponse], summary="الحجوزات المعلقة (أدمن)")
def get_pending_bookings_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """الحصول على الحجوزات المعلقة التي تحتاج موافقة (للأدمن فقط)"""
    
    bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.PENDING
    ).order_by(Booking.created_at.desc()).all()
    
    results = []
    for booking in bookings:
        response = BookingDetailResponse(**booking.__dict__)
        
        if booking.service:
            response.service_name = booking.service.name_ar
        if booking.pool_type:
            response.pool_type_name = booking.pool_type.name_ar
        if booking.package:
            response.package_name = booking.package.name_ar
        if booking.user:
            response.user_name = booking.user.full_name
        
        results.append(response)
    
    return results

@router.put("/admin/bookings/{booking_id}", response_model=BookingResponse, summary="تحديث حجز (أدمن)")
def update_booking_admin(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    تحديث حالة الحجز وإضافة ملاحظات (للأدمن فقط)
    - تأكيد/رفض الحجز
    - تحديث موعد الصيانة القادم
    """
    # TODO: التحقق من أن المستخدم أدمن
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الحجز غير موجود"
        )
    
    update_data = booking_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    
    # TODO: إرسال إشعار للمستخدم بتحديث حالة الحجز
    
    return booking

@router.delete("/admin/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف حجز (أدمن)")
def delete_booking_admin(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """حذف حجز (للأدمن فقط)"""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الحجز غير موجود"
        )
    
    db.delete(booking)
    db.commit()
    return None