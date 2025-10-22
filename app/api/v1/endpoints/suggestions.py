# app/api/v1/endpoints/suggestions.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.booking import Booking
from datetime import datetime, timedelta

router = APIRouter()

@router.get("")
def get_suggestions(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
) -> List[dict]:
    suggestions = []

    # تحقق من وجود حجز "تنظيف"
    cleaning = db.query(Booking).filter(
        Booking.user_id == user_id,
        Booking.service == "تنظيف"
    ).first()

    if cleaning:
        suggestions.append({
            "title": "استمر في نظافة حمامك!",
            "description": "جرب خدمة التنظيف الأسبوعية بخصم 10%.",
            "action_url": "/services/cleaning-weekly"
        })

    # تحقق من آخر حجز (لو قبل شهر)
    last_booking = db.query(Booking).filter(
        Booking.user_id == user_id
    ).order_by(Booking.date.desc()).first()

    if last_booking and last_booking.date < datetime.utcnow() - timedelta(days=30):
        suggestions.append({
            "title": "لماذا لا تحجز الآن؟",
            "description": "عروض جديدة على صيانة الحمامات!",
            "action_url": "/services/maintenance"
        })

    return suggestions