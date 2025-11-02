from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_technician
from app.db.database import get_db
from app.models.booking import Booking
from app.models.enums import BookingStatus, BookingType
from app.models.user import User
from app.schemas.booking import BookingResponse


class TechnicianBookingStatusUpdate(BaseModel):
    status: BookingStatus = Field(..., description="الحالة الجديدة للحجز")
    admin_notes: Optional[str] = Field(
        None,
        description="ملاحظات يضيفها الفني لتحديث الحجز"
    )


router = APIRouter(tags=["Technician"])


@router.get(
    "/bookings/upcoming",
    response_model=List[BookingResponse],
    summary="الحجوزات القادمة للفني"
)
def get_upcoming_bookings_for_technician(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_technician)
):
    """الحجوزات المؤكدة أو الجارية ابتداءً من اليوم."""
    today = date.today()

    bookings = db.query(Booking).filter(
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
        Booking.booking_type != BookingType.CONSTRUCTION,
        Booking.booking_date >= today
    ).order_by(Booking.booking_date, Booking.booking_time).all()

    return bookings


@router.get(
    "/bookings/history",
    response_model=List[BookingResponse],
    summary="سجل الحجوزات المكتملة للفني"
)
def get_completed_bookings_for_technician(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_technician)
):
    """الحجوزات التي تم تنفيذها مسبقاً."""
    bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.COMPLETED,
        Booking.booking_type != BookingType.CONSTRUCTION
    ).order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).all()

    return bookings


@router.patch(
    "/bookings/{booking_id}/status",
    response_model=BookingResponse,
    summary="تحديث حالة الحجز بواسطة الفني"
)
def update_booking_status_by_technician(
    booking_id: int,
    payload: TechnicianBookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_technician)
):
    """تحديث حالة الحجز إلى جاري التنفيذ أو مكتمل بواسطة الفني."""
    if payload.status not in {BookingStatus.IN_PROGRESS, BookingStatus.COMPLETED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يمكن للفني تحديث الحالة إلى جاري التنفيذ أو مكتمل فقط"
        )

    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="الحجز غير موجود")

    if booking.booking_type == BookingType.CONSTRUCTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكن للفني تحديث حجوزات إنشاء المسابح"
        )

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="هذا الحجز ملغي ولا يمكن تحديثه"
        )

    booking.status = payload.status

    if payload.admin_notes is not None:
        booking.admin_notes = payload.admin_notes

    db.commit()
    db.refresh(booking)

    return booking


__all__ = ["router"]
