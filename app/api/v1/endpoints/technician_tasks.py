from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_technician
from app.db.database import get_db
from app.models.service_offer import OfferStatus, ServiceOffer
from app.models.technician_task import TaskPriority, TechnicianTask, TechnicianTaskStatus
from app.models.water_quality import WaterQualityReading
from app.schemas.notification import (
    TechnicianNotificationsFeedResponse,
    TechnicianUpcomingVisit,
)
from app.schemas.pool_profile import PoolProfileResponse
from app.schemas.service_offer import ServiceOfferDetailResponse
from app.schemas.technician_task import (
    ClientDetailsSection,
    TechnicianTaskDetailResponse,
    TechnicianTaskResponse,
)
from app.schemas.water_quality import (
    WaterQualityHistoryResponse,
    WaterQualityReadingCreate,
    WaterQualityReadingResponse,
)
from app.models.user import User

router = APIRouter(prefix="/technician", tags=["Technician Tasks"])

IDEAL_WATER_RANGES = {
    "temperature_c": "24° - 28°",
    "chlorine_ppm": "1.0 - 3.0 ppm",
    "ph_level": "7.2 - 7.6",
}


@router.get(
    "/tasks/{task_id}/details",
    response_model=TechnicianTaskDetailResponse,
    summary="تفاصيل مهمة الفني مع بيانات العميل والمسبح",
)
def get_task_details(
    task_id: int,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> TechnicianTaskDetailResponse:
    task = (
        db.query(TechnicianTask)
        .options(joinedload(TechnicianTask.pool_profile))
        .filter(
            TechnicianTask.id == task_id,
            TechnicianTask.technician_id == current_user.id,
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المهمة غير موجودة أو غير مرتبطة بك",
        )

    client_section = ClientDetailsSection(
        full_name=task.customer_name,
        phone=task.customer_phone,
        avatar=task.customer_avatar,
        location_name=task.location_name,
        location_address=task.location_address,
        latitude=task.location_latitude,
        longitude=task.location_longitude,
        map_url=_build_google_maps_link(
            task.location_latitude, task.location_longitude, task.location_address
        ),
        scheduled_date=task.scheduled_date,
        scheduled_time=task.scheduled_time,
        priority=task.priority,
        status=task.status,
    )

    pool_profile_schema: Optional[PoolProfileResponse] = None
    if task.pool_profile:
        pool_profile_schema = PoolProfileResponse.model_validate(task.pool_profile)

    readings = (
        db.query(WaterQualityReading)
        .filter(WaterQualityReading.task_id == task.id)
        .order_by(WaterQualityReading.recorded_at.desc())
        .all()
    )

    reading_schemas = [_map_reading_to_schema(reading) for reading in readings]
    latest_reading = reading_schemas[0] if reading_schemas else None
    history = reading_schemas[1:] if len(reading_schemas) > 1 else []

    water_quality_section = WaterQualityHistoryResponse(
        latest=latest_reading,
        history=history,
        ideal_ranges=IDEAL_WATER_RANGES,
    )

    return TechnicianTaskDetailResponse(
        task=TechnicianTaskResponse.model_validate(task),
        client=client_section,
        pool_profile=pool_profile_schema,
        water_quality=water_quality_section,
    )


@router.post(
    "/tasks/{task_id}/water-quality",
    response_model=WaterQualityReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="إضافة قراءة جديدة لجودة المياه",
)
def add_water_quality_reading(
    task_id: int,
    payload: WaterQualityReadingCreate,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> WaterQualityReadingResponse:
    task = (
        db.query(TechnicianTask)
        .filter(
            TechnicianTask.id == task_id,
            TechnicianTask.technician_id == current_user.id,
        )
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="لا يمكن إضافة القراءة لهذه المهمة",
        )

    recorded_at = payload.recorded_at
    if recorded_at is None:
        recorded_at = datetime.now(timezone.utc)
    elif recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(tzinfo=timezone.utc)

    reading = WaterQualityReading(
        task_id=task.id,
        technician_id=current_user.id,
        temperature_c=payload.temperature_c,
        chlorine_ppm=payload.chlorine_ppm,
        ph_level=payload.ph_level,
        alkalinity_ppm=payload.alkalinity_ppm,
        salinity_ppm=payload.salinity_ppm,
        notes=payload.notes,
        recorded_at=recorded_at,
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return _map_reading_to_schema(reading)


@router.get(
    "/notifications/feed",
    response_model=TechnicianNotificationsFeedResponse,
    summary="ملخص تنبيهات الفني (المهام القادمة + عروض المتجر)",
)
def get_technician_notifications_feed(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> TechnicianNotificationsFeedResponse:
    today = date.today()
    upcoming_tasks = (
        db.query(TechnicianTask)
        .filter(
            TechnicianTask.technician_id == current_user.id,
            TechnicianTask.status.in_(
                [TechnicianTaskStatus.SCHEDULED, TechnicianTaskStatus.IN_PROGRESS]
            ),
            TechnicianTask.scheduled_date >= today,
        )
        .order_by(
            TechnicianTask.scheduled_date.asc(),
            TechnicianTask.scheduled_time.asc(),
        )
        .limit(15)
        .all()
    )

    reminders = [_map_task_to_upcoming_visit(task) for task in upcoming_tasks]

    offers = (
        db.query(ServiceOffer)
        .options(joinedload(ServiceOffer.service))
        .filter(ServiceOffer.status == OfferStatus.ACTIVE)
        .order_by(
            ServiceOffer.is_featured.desc(),
            ServiceOffer.sort_order.desc(),
            ServiceOffer.created_at.desc(),
        )
        .limit(6)
        .all()
    )
    offer_cards = [_map_offer_to_schema(offer) for offer in offers]

    return TechnicianNotificationsFeedResponse(
        total_upcoming=len(reminders),
        upcoming_visits=reminders,
        store_offers=offer_cards,
        last_refreshed_at=datetime.now(timezone.utc),
    )


def _map_reading_to_schema(reading: WaterQualityReading) -> WaterQualityReadingResponse:
    schema = WaterQualityReadingResponse.model_validate(reading)
    schema.relative_time = _humanize_relative_time(reading.recorded_at)
    return schema


def _map_task_to_upcoming_visit(task: TechnicianTask) -> TechnicianUpcomingVisit:
    scheduled_at = _combine_datetime(task.scheduled_date, task.scheduled_time)
    return TechnicianUpcomingVisit(
        task_id=task.id,
        title=task.title,
        scheduled_date=task.scheduled_date,
        scheduled_time=task.scheduled_time,
        status=task.status,
        priority=task.priority,
        customer_name=task.customer_name,
        location_name=task.location_name,
        location_address=task.location_address,
        map_url=_build_google_maps_link(
            task.location_latitude, task.location_longitude, task.location_address
        ),
        relative_time=_humanize_relative_time(scheduled_at),
        tags=_build_tags(task),
    )


def _map_offer_to_schema(offer: ServiceOffer) -> ServiceOfferDetailResponse:
    schema = ServiceOfferDetailResponse.model_validate(offer)
    if offer.service:
        schema.service_name = offer.service.name_ar
    return schema


def _combine_datetime(
    date_value: Optional[date], time_value: Optional[time]
) -> Optional[datetime]:
    if not date_value:
        return None
    combined_time = time_value or time(hour=9, minute=0)
    return datetime.combine(date_value, combined_time, tzinfo=timezone.utc)


def _build_google_maps_link(
    latitude: Optional[float],
    longitude: Optional[float],
    address: Optional[str],
) -> Optional[str]:
    if latitude is not None and longitude is not None:
        return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    if address:
        from urllib.parse import quote_plus

        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"
    return None


def _humanize_relative_time(moment: Optional[datetime]) -> Optional[str]:
    if not moment:
        return None

    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    delta: timedelta = now - moment

    seconds = int(delta.total_seconds())
    future = seconds < 0
    seconds = abs(seconds)
    minutes = seconds // 60

    prefix = "بعد " if future else "منذ "

    if seconds < 60:
        return "حالاً" if future else "الآن"
    if minutes < 60:
        return f"{prefix}{minutes} دقيقة"

    hours = minutes // 60
    if hours < 24:
        return f"{prefix}{hours} ساعة"

    days = hours // 24
    if days < 7:
        return f"{prefix}{days} يوم"

    weeks = days // 7
    if weeks < 4:
        return f"{prefix}{weeks} أسبوع"

    return moment.strftime("%Y-%m-%d")


def _build_tags(task: TechnicianTask) -> List[str]:
    tags: List[str] = []
    if task.priority == TaskPriority.URGENT:
        tags.append("عاجل")
    elif task.priority == TaskPriority.HIGH:
        tags.append("أولوية مرتفعة")

    if task.status == TechnicianTaskStatus.IN_PROGRESS:
        tags.append("قيد التنفيذ")
    elif task.status == TechnicianTaskStatus.SCHEDULED:
        tags.append("مجدولة")

    if task.location_name:
        tags.append(task.location_name)

    return tags

