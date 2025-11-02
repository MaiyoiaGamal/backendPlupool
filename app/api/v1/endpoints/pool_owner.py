from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints import booking as booking_endpoints
from app.api.v1.endpoints.home import create_home_router
from app.core.dependencies import get_current_pool_owner
from app.db.database import get_db
from app.models.enums import BookingType, BookingStatus
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingDetailResponse,
)


router = APIRouter(tags=["Pool Owner"])

router.include_router(
    create_home_router("صاحب حمام"),
    prefix="/home",
    tags=["Pool Owner Home"]
)


@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="إنشاء حجز جديد (صاحب حمام)"
)
def create_pool_owner_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pool_owner)
):
    """حجز خدمة جديدة لصاحب حمام سباحة."""
    return booking_endpoints.create_booking(
        booking=booking,
        db=db,
        current_user=current_user
    )


@router.get(
    "/bookings",
    response_model=List[BookingResponse],
    summary="قائمة حجوزات صاحب الحمام"
)
def list_pool_owner_bookings(
    booking_type: Optional[BookingType] = Query(None, description="فلترة حسب نوع الحجز"),
    status_filter: Optional[BookingStatus] = Query(None, description="فلترة حسب الحالة"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pool_owner)
):
    """عرض جميع الحجوزات المرتبطة بصاحب الحمام الحالي."""
    return booking_endpoints.get_my_bookings(
        booking_type=booking_type,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
        db=db,
        current_user=current_user
    )


@router.get(
    "/bookings/{booking_id}",
    response_model=BookingDetailResponse,
    summary="تفاصيل حجز لصاحب حمام"
)
def get_pool_owner_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pool_owner)
):
    """عرض تفاصيل حجز معين لصاحب الحمام الحالي."""
    return booking_endpoints.get_my_booking_detail(
        booking_id=booking_id,
        db=db,
        current_user=current_user
    )


@router.get(
    "/bookings/reminders",
    response_model=List[BookingResponse],
    summary="تذكيرات الصيانة القادمة لصاحب الحمام"
)
def get_pool_owner_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pool_owner)
):
    """عرض مواعيد الصيانة القادمة للحجوزات المفعّلة."""
    return booking_endpoints.get_my_maintenance_reminders(
        db=db,
        current_user=current_user
    )


__all__ = ["router"]
