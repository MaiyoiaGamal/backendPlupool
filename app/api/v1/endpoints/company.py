from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints import booking as booking_endpoints
from app.api.v1.endpoints.home import create_home_router
from app.core.dependencies import get_current_company_user
from app.db.database import get_db
from app.models.booking import Booking
from app.models.enums import BookingType, BookingStatus
from app.models.user import User
from app.schemas.booking import (
    BookingDetailResponse,
    BookingResponse,
    BookingUpdate,
)


router = APIRouter(tags=["Company"])

router.include_router(
    create_home_router("شركة"),
    prefix="/home",
    tags=["Company Home"]
)


@router.get(
    "/bookings",
    response_model=List[BookingDetailResponse],
    summary="جميع الحجوزات (الشركة)"
)
def list_company_bookings(
    booking_type: Optional[BookingType] = Query(None, description="فلترة حسب نوع الحجز"),
    status_filter: Optional[BookingStatus] = Query(None, description="فلترة حسب الحالة"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """عرض جميع الحجوزات المتاحة لفريق الشركة."""
    return booking_endpoints.get_all_bookings_admin(
        booking_type=booking_type,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
        db=db,
        current_user=current_user
    )


@router.get(
    "/bookings/pending",
    response_model=List[BookingDetailResponse],
    summary="الحجوزات المعلقة (الشركة)"
)
def list_pending_company_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """عرض الحجوزات التي ما زالت في حالة انتظار التأكيد."""
    return booking_endpoints.get_pending_bookings_admin(
        db=db,
        current_user=current_user
    )


@router.get(
    "/bookings/{booking_id}",
    response_model=BookingDetailResponse,
    summary="تفاصيل حجز (الشركة)"
)
def get_company_booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """عرض تفاصيل حجز معين لتسهيل المتابعة من جانب الشركة."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="الحجز غير موجود")

    response = BookingDetailResponse(**booking.__dict__)

    if booking.service:
        response.service_name = booking.service.name_ar
    if booking.pool_type:
        response.pool_type_name = booking.pool_type.name_ar
    if booking.package:
        response.package_name = booking.package.name_ar
    if booking.user:
        response.user_name = booking.user.full_name

    return response


@router.put(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    summary="تحديث حالة حجز (الشركة)"
)
def update_company_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """تحديث حالة الحجز أو إضافة ملاحظات من قبل الشركة."""
    return booking_endpoints.update_booking_admin(
        booking_id=booking_id,
        booking_update=booking_update,
        db=db,
        current_user=current_user
    )


@router.delete(
    "/bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف حجز (الشركة)"
)
def delete_company_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """حذف حجز لم يعد مطلوباً من قبل الشركة."""
    booking_endpoints.delete_booking_admin(
        booking_id=booking_id,
        db=db,
        current_user=current_user
    )
    return None


__all__ = ["router"]
