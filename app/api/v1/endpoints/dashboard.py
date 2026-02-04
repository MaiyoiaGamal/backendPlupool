from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, nullslast
from sqlalchemy.orm import Session

from app.api.v1.endpoints.home import _fetch_featured_service_offers, _fetch_featured_products
from app.core.config import settings
from app.core.dependencies import (
    get_current_company_user,
    get_current_pool_owner,
    get_current_technician,
)
from app.db.database import get_db
from app.models.booking import Booking, BookingStatus, BookingType
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.product import Product, ProductStatus
from app.models.service import Service, ServiceStatus, ServiceType
from app.models.service_offer import ServiceOffer, OfferStatus
from app.models.technician_task import TechnicianTask, TechnicianTaskStatus
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.dashboard import (
    AccountSection,
    CompanyDashboardResponse,
    FooterNavItem,
    FooterNavigation,
    MetricItem,
    NavBarData,
    ContactChannel,
    NotificationSummary,
    PoolOwnerDashboardResponse,
    ProjectCard,
    OfferCard,
    QuickActionCard,
    SharedHomeSections,
    StoreItemCard,
    TechnicianDashboardResponse,
    TestimonialCard,
    UserSummary,
    WeeklyDayPlan,
    WeeklyOverview,
)
from app.schemas.technician_task import TechnicianTaskResponse


router = APIRouter(prefix="/dashboard", tags=["Dashboards"])


ARABIC_DAY_NAMES = {
    0: "الاثنين",
    1: "الثلاثاء",
    2: "الأربعاء",
    3: "الخميس",
    4: "الجمعة",
    5: "السبت",
    6: "الأحد",
}


def _relative_time(dt: datetime | None) -> str:
    if not dt:
        return ""

    aware_dt = dt
    if dt.tzinfo is not None:
        aware_dt = dt.astimezone(tz=None).replace(tzinfo=None)

    now = datetime.utcnow()
    diff = now - aware_dt

    if diff.days >= 365:
        years = diff.days // 365
        return f"منذ {years} سنة" if years > 1 else "منذ سنة"
    if diff.days >= 30:
        months = diff.days // 30
        return f"منذ {months} شهر" if months > 1 else "منذ شهر"
    if diff.days >= 1:
        return f"منذ {diff.days} يوم"
    hours = diff.seconds // 3600
    if hours >= 1:
        return f"منذ {hours} ساعة"
    minutes = diff.seconds // 60
    if minutes >= 1:
        return f"منذ {minutes} دقيقة"
    return "الآن"


def _build_footer_navigation() -> FooterNavigation:
    items = [
        FooterNavItem(label="الرئيسية", icon="home", target="/home"),
        FooterNavItem(label="الخدمات", icon="services", target="/services"),
        FooterNavItem(label="حمامي", icon="pool", target="/my-pool"),
        FooterNavItem(label="المتجر", icon="store", target="/store"),
        FooterNavItem(label="حسابي", icon="account", target="/account"),
    ]
    return FooterNavigation(items=items)


def _build_contact_channels(user: User) -> List[ContactChannel]:
    whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER or "+201234567890"
    normalized = whatsapp_number.replace("+", "").replace(" ", "")

    channels: List[ContactChannel] = [
        ContactChannel(
            label="واتساب الدعم",
            type="whatsapp",
            value=whatsapp_number,
            link=f"https://wa.me/{normalized}",
        )
    ]

    if user.phone:
        channels.append(
            ContactChannel(
                label="اتصل بنا",
                type="phone",
                value=user.phone,
                link=f"tel:{user.phone}",
            )
        )

    channels.append(
        ContactChannel(
            label="البريد الإلكتروني",
            type="email",
            value="support@plupool.com",
            link="mailto:support@plupool.com",
        )
    )

    return channels


def _build_nav_data(user: User, db: Session) -> NavBarData:
    total_notifications = (
        db.query(func.count(Notification.id)).filter(Notification.user_id == user.id).scalar() or 0
    )
    unread_notifications = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user.id, Notification.is_read.is_(False))
        .scalar()
        or 0
    )

    return NavBarData(
        user=UserSummary(
            id=user.id,
            full_name=user.full_name,
            role=user.role.value,
            phone=user.phone,
            profile_image=user.profile_image,
        ),
        notifications=NotificationSummary(total=total_notifications, unread=unread_notifications),
        contact_channels=_build_contact_channels(user),
    )


def _fetch_quick_actions(db: Session, limit: int = 3) -> List[QuickActionCard]:
    services = (
        db.query(Service)
        .filter(Service.status == ServiceStatus.ACTIVE)
        .order_by(Service.created_at.desc())
        .limit(limit)
        .all()
    )

    cards: List[QuickActionCard] = []
    for service in services:
        cards.append(
            QuickActionCard(
                id=f"service_{service.id}",
                title=service.name_ar,
                subtitle=service.description_ar[:80] if service.description_ar else None,
                image_url=service.image_url,
                target=f"/services/{service.id}",
            )
        )

    if len(cards) < limit:
        cards.append(
            QuickActionCard(
                id="services_root",
                title="كل الخدمات",
                subtitle="استكشف حلول Plupool",
                image_url=None,
                target="/services",
            )
        )
    if len(cards) < limit:
        cards.append(
            QuickActionCard(
                id="store_root",
                title="تسوق معدات المسابح",
                subtitle="منتجات مختارة بعناية",
                image_url=None,
                target="/store",
            )
        )

    return cards[:limit]


def _fetch_special_offers(db: Session, limit: int = 6) -> List[OfferCard]:
    offers = (
        db.query(ServiceOffer)
        .filter(
            ServiceOffer.status == OfferStatus.ACTIVE,
        )
        .order_by(ServiceOffer.is_featured.desc(), ServiceOffer.sort_order.asc(), ServiceOffer.created_at.desc())
        .limit(limit)
        .all()
    )

    offer_cards: List[OfferCard] = []
    for offer in offers:
        offer_cards.append(
            OfferCard(
                id=offer.id,
                title=offer.title_ar,
                description=offer.description_ar,
                badge=offer.badge_text,
                service_id=offer.service_id,
                service_name=offer.service.name_ar if offer.service else None,
                original_price=offer.original_price,
                final_price=offer.final_price,
                image_url=offer.image_url,
            )
        )

    if not offer_cards:
        fetched = _fetch_featured_service_offers(limit=limit, db=db)
        for offer in fetched:
            offer_cards.append(
                OfferCard(
                    id=offer.id,
                    title=offer.title_ar,
                    description=offer.description_ar,
                    badge=offer.badge_text,
                    service_id=offer.service_id,
                    service_name=offer.service_name,
                    original_price=offer.original_price,
                    final_price=offer.final_price,
                    image_url=offer.image_url,
                )
            )

    return offer_cards


def _calc_discount_percentage(original_price: int, final_price: int) -> float | None:
    if not original_price:
        return None
    if original_price <= 0 or final_price is None:
        return None
    try:
        discount = 100 - ((final_price / original_price) * 100)
    except ZeroDivisionError:
        return None
    return round(discount, 1)


def _fetch_store_highlights(db: Session, limit: int = 6) -> List[StoreItemCard]:
    products = (
        db.query(Product)
        .filter(Product.status == ProductStatus.ACTIVE)
        .order_by(Product.is_featured.desc(), Product.sort_order.asc(), Product.created_at.desc())
        .limit(limit)
        .all()
    )

    highlights: List[StoreItemCard] = []
    for product in products:
        discount = _calc_discount_percentage(product.original_price, product.final_price)
        badge = None
        if product.is_featured:
            badge = "الأكثر مبيعًا"
        elif discount and discount > 0:
            badge = f"خصم %{int(discount)}"

        highlights.append(
            StoreItemCard(
                id=product.id,
                title=product.name_ar,
                original_price=product.original_price,
                final_price=product.final_price,
                discount_percentage=discount,
                image_url=product.image_url,
                badge=badge,
                rating=product.rating,
            )
        )

    return highlights


def _fetch_projects(db: Session, limit: int = 5) -> List[ProjectCard]:
    services = (
        db.query(Service)
        .filter(Service.service_type == ServiceType.CONSTRUCTION, Service.status == ServiceStatus.ACTIVE)
        .order_by(Service.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        ProjectCard(
            id=service.id,
            title=service.name_ar,
            description=service.description_ar,
            image_url=service.image_url,
            category=service.service_type.value,
        )
        for service in services
    ]


def _fetch_general_testimonials(db: Session, limit: int = 6) -> List[TestimonialCard]:
    comments = (
        db.query(Comment)
        .join(User, Comment.user_id == User.id)
        .order_by(Comment.created_at.desc())
        .limit(limit)
        .all()
    )

    testimonials: List[TestimonialCard] = []
    for comment in comments:
        testimonials.append(
            TestimonialCard(
                id=comment.id,
                user_name=comment.user.full_name if comment.user else "عميل Plupool",
                user_avatar=comment.user.profile_image if comment.user else None,
                rating=comment.rating,
                message=comment.content,
                created_at=comment.created_at,
                relative_time=_relative_time(comment.created_at),
            )
        )

    return testimonials


def _build_shared_sections(db: Session) -> SharedHomeSections:
    quick_actions = _fetch_quick_actions(db)
    offer_cards = _fetch_special_offers(db)
    store_highlights = _fetch_store_highlights(db, limit=6)
    testimonials = _fetch_general_testimonials(db)
    projects = _fetch_projects(db)

    return SharedHomeSections(
        quick_actions=quick_actions,
        special_offers=offer_cards,
        store_highlights=store_highlights,
        testimonials=testimonials,
        projects=projects,
    )


def _build_owner_account_section(user: User, db: Session) -> AccountSection:
    base_query = db.query(Booking).filter(Booking.user_id == user.id)
    total_bookings = base_query.count()

    active_bookings = (
        base_query.filter(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])).count()
    )
    pending_bookings = base_query.filter(Booking.status == BookingStatus.PENDING).count()

    today = date.today()
    upcoming = (
        base_query.filter(
            Booking.booking_date >= today,
            Booking.booking_date <= today + timedelta(days=7),
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
        ).count()
    )
    active_packages = (
        base_query.filter(
            Booking.booking_type == BookingType.MAINTENANCE_PACKAGE,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
        ).count()
    )

    metrics = [
        MetricItem(key="total_bookings", label="إجمالي الحجوزات", value=total_bookings),
        MetricItem(key="active_bookings", label="الحجوزات النشطة", value=active_bookings),
        MetricItem(key="upcoming_week", label="هذا الأسبوع", value=upcoming),
        MetricItem(key="pending_requests", label="بانتظار التأكيد", value=pending_bookings),
        MetricItem(key="active_packages", label="باقات الصيانة", value=active_packages),
    ]

    return AccountSection(title="حسابي", metrics=metrics)


def _build_company_account_section(db: Session) -> AccountSection:
    total_clients = db.query(func.count(func.distinct(Booking.user_id))).scalar() or 0
    active_projects = (
        db.query(func.count(Booking.id))
        .filter(Booking.status.in_([BookingStatus.IN_PROGRESS, BookingStatus.CONFIRMED]))
        .scalar()
        or 0
    )
    pending_requests = (
        db.query(func.count(Booking.id)).filter(Booking.status == BookingStatus.PENDING).scalar() or 0
    )
    technician_count = (
        db.query(func.count(User.id)).filter(User.role == UserRole.TECHNICIAN).scalar() or 0
    )

    avg_rating = db.query(func.avg(Comment.rating)).scalar()
    rating_value = round(float(avg_rating), 1) if avg_rating else 0.0

    metrics = [
        MetricItem(key="clients", label="العملاء", value=total_clients),
        MetricItem(key="active_projects", label="مشاريع نشطة", value=active_projects),
        MetricItem(key="pending_requests", label="طلبات قيد الانتظار", value=pending_requests),
        MetricItem(key="team_size", label="عدد الفنيين", value=technician_count),
        MetricItem(key="avg_rating", label="متوسط التقييم", value=rating_value, unit="⭐"),
    ]

    return AccountSection(title="لوحة الشركة", metrics=metrics)


def _group_tasks_by_date(tasks: List[TechnicianTask]) -> dict[date, List[TechnicianTask]]:
    grouped: dict[date, List[TechnicianTask]] = defaultdict(list)
    for task in tasks:
        grouped[task.scheduled_date].append(task)
    for task_list in grouped.values():
        task_list.sort(key=lambda t: (t.scheduled_time or datetime.min.time(), t.id))
    return grouped


def _build_weekly_overview(user: User, db: Session) -> WeeklyOverview:
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    tasks = (
        db.query(TechnicianTask)
        .filter(
            TechnicianTask.technician_id == user.id,
            TechnicianTask.scheduled_date >= start_of_week,
            TechnicianTask.scheduled_date <= end_of_week,
        )
        .all()
    )

    grouped = _group_tasks_by_date(tasks)

    days: List[WeeklyDayPlan] = []
    for offset in range(7):
        current_date = start_of_week + timedelta(days=offset)
        day_tasks = [
            TechnicianTaskResponse.model_validate(task)
            for task in grouped.get(current_date, [])
        ]
        label = ARABIC_DAY_NAMES.get(current_date.weekday(), current_date.strftime("%A"))
        days.append(
            WeeklyDayPlan(
                date=current_date,
                label=label,
                is_today=current_date == today,
                tasks=day_tasks,
            )
        )

    empty_state_message = None
    if all(not day.tasks for day in days):
        empty_state_message = "النهاردة بريك 😎"

    return WeeklyOverview(
        start_date=start_of_week,
        end_date=end_of_week,
        days=days,
        empty_state_message=empty_state_message,
    )


def _build_technician_stats(user: User, db: Session, overview: WeeklyOverview) -> AccountSection:
    completed_count = (
        db.query(func.count(TechnicianTask.id))
        .filter(
            TechnicianTask.technician_id == user.id,
            TechnicianTask.status == TechnicianTaskStatus.COMPLETED,
        )
        .scalar()
        or 0
    )

    avg_rating = (
        db.query(func.avg(TechnicianTask.client_rating))
        .filter(
            TechnicianTask.technician_id == user.id,
            TechnicianTask.client_rating.isnot(None),
        )
        .scalar()
    )
    rating_value = round(float(avg_rating), 1) if avg_rating else 0.0

    weekly_tasks_count = sum(len(day.tasks) for day in overview.days)
    active_week_tasks = sum(
        1
        for day in overview.days
        for task in day.tasks
        if task.status != TechnicianTaskStatus.COMPLETED
    )

    metrics = [
        MetricItem(key="rating", label="التقييم", value=rating_value, unit="⭐"),
        MetricItem(key="weekly_tasks", label="مهام الأسبوع", value=weekly_tasks_count),
        MetricItem(key="active_week", label="مهام قيد التنفيذ", value=active_week_tasks),
        MetricItem(key="completed_tasks", label="المهام المكتملة", value=completed_count),
    ]

    return AccountSection(title="ملخص الفني", metrics=metrics)


def _fetch_completed_tasks(user: User, db: Session, limit: int = 10) -> List[TechnicianTaskResponse]:
    tasks = (
        db.query(TechnicianTask)
        .filter(
            TechnicianTask.technician_id == user.id,
            TechnicianTask.status == TechnicianTaskStatus.COMPLETED,
        )
        .order_by(
            nullslast(TechnicianTask.completed_at.desc()),
            TechnicianTask.updated_at.desc(),
        )
        .limit(limit)
        .all()
    )
    return [TechnicianTaskResponse.model_validate(task) for task in tasks]


def _fetch_technician_testimonials(user: User, db: Session, limit: int = 6) -> List[TestimonialCard]:
    tasks = (
        db.query(TechnicianTask)
        .filter(
            TechnicianTask.technician_id == user.id,
            TechnicianTask.client_feedback.isnot(None),
            TechnicianTask.client_feedback != "",
        )
        .order_by(
            nullslast(TechnicianTask.completed_at.desc()),
            TechnicianTask.updated_at.desc(),
        )
        .limit(limit)
        .all()
    )

    testimonials: List[TestimonialCard] = []
    for task in tasks:
        testimonials.append(
            TestimonialCard(
                id=task.id,
                user_name=task.customer_name or "عميل Plupool",
                user_avatar=task.customer_avatar,
                rating=task.client_rating or 5,
                message=task.client_feedback or "",
                created_at=task.completed_at or task.created_at,
                relative_time=_relative_time(task.completed_at or task.created_at),
            )
        )

    if testimonials:
        return testimonials

    return _fetch_general_testimonials(db, limit=limit)


@router.get("/pool-owner/home", response_model=PoolOwnerDashboardResponse)
def get_pool_owner_dashboard(
    current_user: User = Depends(get_current_pool_owner),
    db: Session = Depends(get_db),
):
    nav = _build_nav_data(current_user, db)
    footer = _build_footer_navigation()
    shared = _build_shared_sections(db)
    account = _build_owner_account_section(current_user, db)

    return PoolOwnerDashboardResponse(
        nav=nav,
        footer=footer,
        shared=shared,
        my_account=account,
    )


@router.get("/company/home", response_model=CompanyDashboardResponse)
def get_company_dashboard(
    current_user: User = Depends(get_current_company_user),
    db: Session = Depends(get_db),
):
    nav = _build_nav_data(current_user, db)
    footer = _build_footer_navigation()
    shared = _build_shared_sections(db)
    account = _build_company_account_section(db)

    return CompanyDashboardResponse(
        nav=nav,
        footer=footer,
        shared=shared,
        my_account=account,
    )


@router.get("/technician/home", response_model=TechnicianDashboardResponse)
def get_technician_dashboard(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
):
    nav = _build_nav_data(current_user, db)
    footer = _build_footer_navigation()
    weekly_overview = _build_weekly_overview(current_user, db)
    stats = _build_technician_stats(current_user, db, weekly_overview)
    completed_tasks = _fetch_completed_tasks(current_user, db)
    store_highlights = _fetch_store_highlights(db, limit=6)
    projects = _fetch_projects(db)
    testimonials = _fetch_technician_testimonials(current_user, db)

    return TechnicianDashboardResponse(
        nav=nav,
        footer=footer,
        stats=stats,
        weekly_overview=weekly_overview,
        completed_tasks=completed_tasks,
        store_highlights=store_highlights,
        projects=projects,
        testimonials=testimonials,
    )


__all__ = [
    "router",
]
