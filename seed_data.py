"""
Populate the Plupool database with opinionated demo data so the API, dashboards,
and mobile flows have something meaningful to render right after setup.

Usage:
    python seed_data.py

The script relies on the DATABASE_URL value from .env, automatically creates the
tables if they don't exist yet, and then inserts (or skips) seed rows so it can
be executed multiple times without duplicating records.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, time, timezone
from typing import Dict, Tuple

from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.models.booking import Booking
from app.models.comment import Comment
from app.models.contact_message import ContactMessage
from app.models.enums import BookingStatus, BookingType, UserRole
from app.models.maintenance_package import MaintenancePackage, PackageDuration
from app.models.notification import Notification
from app.models.pool_type import PoolType
from app.models.product import (
    Product,
    ProductStatus,
    DiscountType as ProductDiscountType,
)
from app.models.category import Category
from app.models.service import Service, ServiceStatus, ServiceType
from app.models.service_offer import (
    ServiceOffer,
    OfferStatus,
    DiscountType as OfferDiscountType,
)
from app.models.technician_task import (
    TechnicianTask,
    TechnicianTaskStatus,
    TaskPriority,
)
from app.models.client_pool_profile import ClientPoolProfile
from app.models.user import User
from app.models.water_quality import WaterQualityReading
from app.models.faq import FAQ
from app.models.privacy_policy import PrivacyPolicySection
from app.models.why_us import WhyUsStat, WhyUsFeature

logger = logging.getLogger("plupool.seed")


def _get_or_create(
    session: Session,
    model,
    *,
    filters: Dict,
    defaults: Dict | None = None,
):
    instance = session.query(model).filter_by(**filters).first()
    if instance:
        return instance, False
    payload = dict(defaults or {})
    payload.update(filters)
    instance = model(**payload)
    session.add(instance)
    session.flush()
    return instance, True


def seed_users(session: Session) -> Tuple[Dict[str, User], int]:
    users_data = [
        (
            "pool_owner",
            {
                "phone": "+201000000101",
                "full_name": "أحمد عبد الله",
                "profile_image": "https://images.plupool.app/users/ahmed.png",
                "role": UserRole.POOL_OWNER,
                "address": "التجمع الخامس، القاهرة الجديدة",
                "latitude": 30.02,
                "longitude": 31.48,
                "is_phone_verified": True,
                "is_active": True,
                "is_approved": True,
            },
        ),
        (
            "technician",
            {
                "phone": "+201000000202",
                "full_name": "محمود حسن",
                "profile_image": "https://images.plupool.app/users/mahmoud-tech.png",
                "role": UserRole.TECHNICIAN,
                "address": "مدينة نصر، القاهرة",
                "latitude": 30.06,
                "longitude": 31.33,
                "skills": "تنظيف شامل, معالجة المياه, فحص معدات",
                "years_of_experience": 8,
                "is_phone_verified": True,
                "is_active": True,
                "is_approved": True,
            },
        ),
        (
            "company",
            {
                "phone": "+201000000303",
                "full_name": "شركة بلو بول",
                "profile_image": "https://images.plupool.app/users/company.png",
                "role": UserRole.COMPANY,
                "address": "الشيخ زايد - الجيزة",
                "is_phone_verified": True,
                "is_active": True,
                "is_approved": True,
            },
        ),
    ]

    lookup: Dict[str, User] = {}
    created = 0

    for key, payload in users_data:
        data = payload.copy()
        phone = data.pop("phone")
        user, was_created = _get_or_create(
            session,
            User,
            filters={"phone": phone},
            defaults=data,
        )
        lookup[key] = user
        if was_created:
            created += 1

    return lookup, created


def seed_services(session: Session) -> Tuple[Dict[str, Service], int]:
    services_data = [
        (
            "deep_cleaning",
            {
                "name_ar": "تنظيف شامل للمسابح",
                "name_en": "Premium Pool Deep Cleaning",
                "description_ar": "تنظيف شامل للجدران والأرضية مع إزالة الشوائب والطحالب.",
                "description_en": "Full vacuum, brushing, and skimmer cleaning visit.",
                "service_type": ServiceType.MAINTENANCE,
                "price": 850,
                "icon": "cleaning-kit",
                "image_url": "https://images.plupool.app/services/deep-clean.png",
                "status": ServiceStatus.ACTIVE,
            },
        ),
        (
            "water_balance",
            {
                "name_ar": "معالجة توازن المياه",
                "name_en": "Water Balancing & Testing",
                "description_ar": "تحليل كيميائي كامل وضبط نسب الكلور والـ pH.",
                "description_en": "On-site chemical balancing with digital reporting.",
                "service_type": ServiceType.MAINTENANCE,
                "price": 650,
                "icon": "ph-meter",
                "image_url": "https://images.plupool.app/services/water-balance.png",
                "status": ServiceStatus.ACTIVE,
            },
        ),
        (
            "equipment_care",
            {
                "name_ar": "فحص وصيانة المعدات",
                "name_en": "Pump & Equipment Check",
                "description_ar": "فحص المضخات والفلاتر مع إصلاحات سريعة عند الحاجة.",
                "description_en": "Full mechanical inspection for pumps, filters and heaters.",
                "service_type": ServiceType.MAINTENANCE,
                "price": 950,
                "icon": "tools",
                "image_url": "https://images.plupool.app/services/equipment.png",
                "status": ServiceStatus.ACTIVE,
            },
        ),
        (
            "garden_pool",
            {
                "name_ar": "إنشاء مسبح حديقة عائلية",
                "name_en": "Family Garden Pool Construction",
                "description_ar": "تصميم وبناء مسبح عائلي مع إضاءة محيطية وخيارات تدفئة.",
                "description_en": "Family-sized concrete pool with optional spa corner.",
                "service_type": ServiceType.CONSTRUCTION,
                "price": 185000,
                "icon": "garden-pool",
                "image_url": "https://images.plupool.app/services/garden-pool.png",
                "status": ServiceStatus.ACTIVE,
            },
        ),
        (
            "spa_pool",
            {
                "name_ar": "إنشاء مسبح سبا صغير",
                "name_en": "Compact Spa Pool",
                "description_ar": "حل مثالي للمساحات الصغيرة مع شلال جداري وإضاءة LED.",
                "description_en": "Compact hydrotherapy pool for rooftops and terraces.",
                "service_type": ServiceType.CONSTRUCTION,
                "price": 142000,
                "icon": "spa",
                "image_url": "https://images.plupool.app/services/spa.png",
                "status": ServiceStatus.ACTIVE,
            },
        ),
        (
            "seasonal_contract",
            {
                "name_ar": "صيانة موسمية متقدمة",
                "name_en": "Seasonal Maintenance Contract",
                "description_ar": "خطة صيانة كاملة مع زيارات إضافية قبل الصيف وبعده.",
                "description_en": "Proactive maintenance bundle with emergency response.",
                "service_type": ServiceType.MAINTENANCE,
                "price": 2100,
                "icon": "calendar",
                "image_url": "https://images.plupool.app/services/seasonal.png",
                "status": ServiceStatus.ACTIVE,
            },
        ),
    ]

    lookup: Dict[str, Service] = {}
    created = 0

    for key, payload in services_data:
        data = payload.copy()
        filters = {"name_ar": data.pop("name_ar")}
        service, was_created = _get_or_create(
            session,
            Service,
            filters=filters,
            defaults=data,
        )
        lookup[key] = service
        if was_created:
            created += 1

    return lookup, created


def seed_pool_types(session: Session) -> Tuple[Dict[str, PoolType], int]:
    pool_types_data = [
        (
            "family_pool",
            {
                "name_ar": "مسبح حديقة عائلية",
                "name_en": "Family Outdoor Pool",
                "description_ar": "تصميم مستطيل مع درج جانبي ومساحة للجلوس.",
                "description_en": "Classic 7x4m pool with seating ledge and LED strip.",
                "image_url": "https://images.plupool.app/pool-types/family.png",
                "length_meters": 7.0,
                "width_meters": 4.0,
                "depth_meters": 2.0,
                "features": [
                    "إضاءة LED ملونة",
                    "مقعد استرخاء",
                    "سلم أمان ستانلس",
                ],
                "suitable_for": "الحدائق المنزلية ومساحات العائلات المتوسطة.",
                "base_price": 165000,
                "is_active": True,
            },
        ),
        (
            "infinity_pool",
            {
                "name_ar": "مسبح لا متناهي",
                "name_en": "Infinity Edge Pool",
                "description_ar": "حافة انسيابية مطلة على الحديقة لإحساس فخم.",
                "description_en": "12m overflow edge pool with hidden surge tank.",
                "image_url": "https://images.plupool.app/pool-types/infinity.png",
                "length_meters": 12.0,
                "width_meters": 5.0,
                "depth_meters": 2.2,
                "features": [
                    "حافة لا متناهية",
                    "مضخات مزدوجة",
                    "نظام تحكم ذكي",
                ],
                "suitable_for": "الفلل الواسعة والفنادق البوتيك.",
                "base_price": 320000,
                "is_active": True,
            },
        ),
        (
            "indoor_pool",
            {
                "name_ar": "مسبح داخلي مغطى",
                "name_en": "Indoor Heated Pool",
                "description_ar": "مسبح مغطى قابل للتدفئة مع معالجة رطوبة.",
                "description_en": "6x3m indoor pool with dehumidifier and skylight.",
                "image_url": "https://images.plupool.app/pool-types/indoor.png",
                "length_meters": 6.0,
                "width_meters": 3.0,
                "depth_meters": 1.6,
                "features": [
                    "نظام تدفئة",
                    "زجاج مزدوج",
                    "سقف سكاي لايت",
                ],
                "suitable_for": "المنازل الخاصة والنوادي الصحية.",
                "base_price": 210000,
                "is_active": True,
            },
        ),
        (
            "kids_pool",
            {
                "name_ar": "مسبح أطفال ترفيهي",
                "name_en": "Kids Splash Pool",
                "description_ar": "عمق آمن مع ألعاب مائية ونوافير صغيرة.",
                "description_en": "Shallow splash pad with interactive fountains.",
                "image_url": "https://images.plupool.app/pool-types/kids.png",
                "length_meters": 4.0,
                "width_meters": 4.0,
                "depth_meters": 0.8,
                "features": [
                    "أرضية مطاطية",
                    "نوافير تفاعلية",
                    "مظلة حماية من الشمس",
                ],
                "suitable_for": "النوادي العائلية ومناطق اللعب.",
                "base_price": 95000,
                "is_active": True,
            },
        ),
    ]

    lookup: Dict[str, PoolType] = {}
    created = 0

    for key, payload in pool_types_data:
        data = payload.copy()
        filters = {"name_ar": data.pop("name_ar")}
        pool_type, was_created = _get_or_create(
            session,
            PoolType,
            filters=filters,
            defaults=data,
        )
        lookup[key] = pool_type
        if was_created:
            created += 1

    return lookup, created


def seed_packages(session: Session) -> Tuple[Dict[str, MaintenancePackage], int]:
    packages_data = [
        (
            "monthly",
            {
                "name_ar": "الباقة الشهرية",
                "name_en": "Monthly Maintenance",
                "description_ar": "4 زيارات شهرياً مع متابعة جودة المياه والتذكير التلقائي.",
                "duration": PackageDuration.MONTHLY,
                "included_services": [
                    "تنظيف شامل",
                    "اختبار كيميائي",
                    "تنظيف الفلاتر",
                ],
                "price": 1200,
                "visits_count": 4,
                "reminder_days_before": 3,
                "is_active": True,
            },
        ),
        (
            "quarterly",
            {
                "name_ar": "باقة 4 شهور",
                "name_en": "Quarterly Care",
                "description_ar": "16 زيارة مع تقارير حالة شهرية ومتابعة للمضخات.",
                "duration": PackageDuration.QUARTERLY,
                "included_services": [
                    "تنظيف شامل",
                    "معالجة كيميائية موسعة",
                    "فحص معدات شهري",
                ],
                "price": 4300,
                "visits_count": 16,
                "reminder_days_before": 3,
                "is_active": True,
            },
        ),
        (
            "yearly",
            {
                "name_ar": "الباقة السنوية",
                "name_en": "Yearly Premium Plan",
                "description_ar": "48 زيارة، دعم طوارئ، وتذكير تلقائي قبل كل صيانة.",
                "duration": PackageDuration.YEARLY,
                "included_services": [
                    "تنظيف شامل",
                    "فحص معدات متقدم",
                    "تقارير شهرية",
                    "زيارة طوارئ مجانية",
                ],
                "price": 12000,
                "visits_count": 48,
                "reminder_days_before": 5,
                "is_active": True,
            },
        ),
    ]

    lookup: Dict[str, MaintenancePackage] = {}
    created = 0

    for key, payload in packages_data:
        data = payload.copy()
        filters = {"duration": data.pop("duration")}
        package, was_created = _get_or_create(
            session,
            MaintenancePackage,
            filters=filters,
            defaults=data,
        )
        lookup[key] = package
        if was_created:
            created += 1

    return lookup, created


def seed_categories(session: Session) -> Tuple[Dict[str, Category], int]:
    categories_data = [
        (
            "cleaning_tools",
            {
                "name_ar": "معدات التنظيف",
                "name_en": "Cleaning Gear",
                "icon": "broom",
                "is_active": True,
            },
        ),
        (
            "lighting",
            {
                "name_ar": "الإضاءة والحساسات",
                "name_en": "Lighting & Sensors",
                "icon": "light",
                "is_active": True,
            },
        ),
        (
            "accessories",
            {
                "name_ar": "إكسسوارات وترفيه",
                "name_en": "Accessories & Wellness",
                "icon": "sparkles",
                "is_active": True,
            },
        ),
    ]

    lookup: Dict[str, Category] = {}
    created = 0

    for key, payload in categories_data:
        data = payload.copy()
        filters = {"name_ar": data.pop("name_ar")}
        category, was_created = _get_or_create(
            session,
            Category,
            filters=filters,
            defaults=data,
        )
        lookup[key] = category
        if was_created:
            created += 1

    return lookup, created


def seed_products(
    session: Session,
    categories: Dict[str, Category],
) -> int:
    products_data = [
        {
            "name_ar": "روبوت تنظيف ذكي",
            "name_en": "Smart Pool Robot",
            "description_ar": "روبوت يعمل عبر Wi-Fi مع قدرة تسلق الجدران وتنظيف القاع.",
            "category_key": "cleaning_tools",
            "original_price": 9500,
            "discount_type": ProductDiscountType.PERCENTAGE,
            "discount_value": 15,
            "image_url": "https://images.plupool.app/products/robot.png",
            "images": [
                "https://images.plupool.app/products/robot-1.png",
                "https://images.plupool.app/products/robot-2.png",
            ],
            "stock_quantity": 8,
            "delivery_time": "48 ساعة",
            "free_delivery": True,
            "rating": 4.9,
            "reviews_count": 132,
            "status": ProductStatus.ACTIVE,
            "is_featured": True,
        },
        {
            "name_ar": "كشاف LED للمسابح",
            "name_en": "RGB Pool LED Light",
            "description_ar": "إضاءة متعددة الألوان متوافقة مع أنظمة التحكم الذكية.",
            "category_key": "lighting",
            "original_price": 1800,
            "discount_type": ProductDiscountType.FIXED,
            "discount_value": 250,
            "image_url": "https://images.plupool.app/products/led.png",
            "images": [
                "https://images.plupool.app/products/led-1.png",
            ],
            "stock_quantity": 25,
            "delivery_time": "24 ساعة",
            "free_delivery": False,
            "rating": 4.6,
            "reviews_count": 87,
            "status": ProductStatus.ACTIVE,
            "is_featured": False,
        },
        {
            "name_ar": "مجموعة اختبارات المياه الشاملة",
            "name_en": "Pro Water Test Kit",
            "description_ar": "مجموعة متكاملة لقياس الـ pH، الكلور، القلوية والملوحة.",
            "category_key": "cleaning_tools",
            "original_price": 550,
            "discount_type": None,
            "discount_value": None,
            "image_url": "https://images.plupool.app/products/test-kit.png",
            "images": [
                "https://images.plupool.app/products/test-kit-1.png",
            ],
            "stock_quantity": 60,
            "delivery_time": "24 ساعة",
            "free_delivery": True,
            "rating": 4.8,
            "reviews_count": 245,
            "status": ProductStatus.ACTIVE,
            "is_featured": False,
        },
        {
            "name_ar": "شلال ستانلس جداري",
            "name_en": "Stainless Wall Waterfall",
            "description_ar": "شلال زخرفي مع إمكانية ربطه بمضخة المسبح الأساسية.",
            "category_key": "accessories",
            "original_price": 7200,
            "discount_type": ProductDiscountType.PERCENTAGE,
            "discount_value": 10,
            "image_url": "https://images.plupool.app/products/waterfall.png",
            "images": [
                "https://images.plupool.app/products/waterfall-1.png",
            ],
            "stock_quantity": 5,
            "delivery_time": "5 أيام",
            "free_delivery": True,
            "rating": 4.7,
            "reviews_count": 41,
            "status": ProductStatus.ACTIVE,
            "is_featured": True,
        },
    ]

    created = 0

    for payload in products_data:
        data = payload.copy()
        category_key = data.pop("category_key")
        category = categories[category_key]
        data["category_id"] = category.id
        images = data.pop("images")
        data["images"] = json.dumps(images)
        filters = {"name_ar": data.pop("name_ar")}
        existing = session.query(Product).filter_by(**filters).first()
        if existing:
            continue
        product = Product(name_ar=filters["name_ar"], **data)
        product.final_price = product.calculate_final_price()
        session.add(product)
        session.flush()
        created += 1

    return created


def seed_offers(
    session: Session,
    services: Dict[str, Service],
) -> int:
    offers_data = [
        {
            "title_ar": "خصم تنظيف بداية الصيف",
            "title_en": "Summer Refresh Offer",
            "description_ar": "وفر 20٪ على أول زيارة تنظيف شاملة قبل موسم الصيف.",
            "service_key": "deep_cleaning",
            "original_price": 1200,
            "discount_type": OfferDiscountType.PERCENTAGE,
            "discount_value": 20,
            "badge_text": "وفر 20%",
            "image_url": "https://images.plupool.app/offers/summer-clean.png",
            "start_date": date(2024, 5, 1),
            "end_date": date(2024, 8, 31),
            "status": OfferStatus.ACTIVE,
            "is_featured": True,
            "sort_order": 1,
        },
        {
            "title_ar": "باقة توازن المياه + فحص مجاني",
            "title_en": "Water Balancing Bundle",
            "description_ar": "فحص معدات مجاني عند حجز خدمة معالجة المياه.",
            "service_key": "water_balance",
            "original_price": 900,
            "discount_type": OfferDiscountType.PERCENTAGE,
            "discount_value": 15,
            "badge_text": "توازن مثالي",
            "image_url": "https://images.plupool.app/offers/water.png",
            "start_date": date(2024, 4, 1),
            "end_date": date(2024, 12, 31),
            "status": OfferStatus.ACTIVE,
            "is_featured": True,
            "sort_order": 2,
        },
        {
            "title_ar": "فحص معدات مجاني مع كل عقد صيانة",
            "title_en": "Equipment Check Bonus",
            "description_ar": "خصم 200 جنيه على زيارة فحص المعدات لعملاء Plupool.",
            "service_key": "equipment_care",
            "original_price": 900,
            "discount_type": OfferDiscountType.FIXED,
            "discount_value": 200,
            "badge_text": "زيارة مجانية",
            "image_url": "https://images.plupool.app/offers/equipment.png",
            "start_date": date(2024, 1, 1),
            "end_date": date(2025, 3, 31),
            "status": OfferStatus.ACTIVE,
            "is_featured": False,
            "sort_order": 3,
        },
    ]

    created = 0

    for payload in offers_data:
        data = payload.copy()
        service = services[data.pop("service_key")]
        filters = {"title_ar": data.pop("title_ar")}
        existing = session.query(ServiceOffer).filter_by(**filters).first()
        if existing:
            continue
        offer = ServiceOffer(title_ar=filters["title_ar"], service_id=service.id, **data)
        offer.final_price = offer.calculate_final_price()
        session.add(offer)
        session.flush()
        created += 1

    return created


def seed_bookings(
    session: Session,
    users: Dict[str, User],
    services: Dict[str, Service],
    pool_types: Dict[str, PoolType],
    packages: Dict[str, MaintenancePackage],
) -> Tuple[Dict[str, Booking], int]:
    bookings_data = [
        (
            "construction_booking",
            {
                "booking_type": BookingType.CONSTRUCTION,
                "status": BookingStatus.PENDING,
                "booking_date": date(2025, 1, 15),
                "booking_time": time(10, 30),
                "pool_type_key": "family_pool",
                "custom_length": 7.0,
                "custom_width": 4.0,
                "custom_depth": 2.0,
                "admin_notes": "أرغب في مسبح بديكور حجري وحديقة جانبية.",
            },
        ),
        (
            "maintenance_single_booking",
            {
                "booking_type": BookingType.MAINTENANCE_SINGLE,
                "status": BookingStatus.CONFIRMED,
                "booking_date": date(2025, 1, 10),
                "booking_time": time(9, 0),
                "service_key": "deep_cleaning",
                "admin_notes": "تنظيف شامل قبل حفل عائلي.",
            },
        ),
        (
            "package_booking",
            {
                "booking_type": BookingType.MAINTENANCE_PACKAGE,
                "status": BookingStatus.IN_PROGRESS,
                "booking_date": date(2025, 1, 5),
                "booking_time": time(8, 30),
                "package_key": "monthly",
                "admin_notes": "متابعة شهرية مع نفس الفني.",
                "next_maintenance_date": date(2025, 2, 4),
            },
        ),
    ]

    user = users["pool_owner"]
    lookup: Dict[str, Booking] = {}
    created = 0

    for key, payload in bookings_data:
        data = payload.copy()
        service_key = data.pop("service_key", None)
        pool_type_key = data.pop("pool_type_key", None)
        package_key = data.pop("package_key", None)

        data["user_id"] = user.id
        if service_key:
            data["service_id"] = services[service_key].id
        if pool_type_key:
            data["pool_type_id"] = pool_types[pool_type_key].id
        if package_key:
            data["package_id"] = packages[package_key].id

        filters = {
            "user_id": data["user_id"],
            "booking_type": data["booking_type"],
            "booking_date": data["booking_date"],
            "booking_time": data["booking_time"],
            "service_id": data.get("service_id"),
            "pool_type_id": data.get("pool_type_id"),
            "package_id": data.get("package_id"),
        }

        existing = (
            session.query(Booking)
            .filter_by(**filters)
            .first()
        )
        if existing:
            lookup[key] = existing
            continue

        booking = Booking(**data)
        session.add(booking)
        session.flush()
        lookup[key] = booking
        created += 1

    return lookup, created


def seed_comments(
    session: Session,
    users: Dict[str, User],
    bookings: Dict[str, Booking],
    services: Dict[str, Service],
) -> int:
    comments_data = [
        {
            "content": "خدمة احترافية وسرعة في الإنجاز. أوصي بها بشدة!",
            "rating": 5,
            "booking_key": "maintenance_single_booking",
            "service_key": "deep_cleaning",
        },
        {
            "content": "متابعة ممتازة للباقات الشهرية وتذكير قبل كل زيارة.",
            "rating": 4,
            "booking_key": "package_booking",
            "service_key": "water_balance",
        },
    ]

    user = users["pool_owner"]
    created = 0

    for payload in comments_data:
        data = payload.copy()
        booking = bookings[data.pop("booking_key")]
        service = services[data.pop("service_key")]
        filters = {
            "user_id": user.id,
            "content": data["content"],
        }
        existing = session.query(Comment).filter_by(**filters).first()
        if existing:
            continue
        comment = Comment(
            user_id=user.id,
            booking_id=booking.id,
            service_id=service.id,
            **data,
        )
        session.add(comment)
        created += 1

    return created


def seed_notifications(
    session: Session,
    users: Dict[str, User],
) -> int:
    now = datetime.now(timezone.utc)
    notifications_data = [
        {
            "user_key": "pool_owner",
            "title": "تم تأكيد حجز التنظيف",
            "message": "قمنا بتأكيد زيارة الفني يوم 10 يناير الساعة 9 صباحاً.",
            "type": "booking",
            "created_at": now,
        },
        {
            "user_key": "pool_owner",
            "title": "تذكير موعد الصيانة",
            "message": "موعد الصيانة الدورية يوم 5 فبراير. تأكد من توافر شخص للاستقبال.",
            "type": "reminder",
            "created_at": now,
        },
        {
            "user_key": "technician",
            "title": "مهمة جديدة بانتظارك",
            "message": "تمت إضافة زيارة عاجلة في التجمع الخامس.",
            "type": "task",
            "created_at": now,
        },
        {
            "user_key": "company",
            "title": "طلب إنشاء مسبح جديد",
            "message": "عميل جديد طلب مسبح حديقة. راجع لوحة التحكم.",
            "type": "lead",
            "created_at": now,
        },
    ]

    created = 0

    for payload in notifications_data:
        data = payload.copy()
        user = users[data.pop("user_key")]
        filters = {"user_id": user.id, "title": data["title"]}
        existing = session.query(Notification).filter_by(**filters).first()
        if existing:
            continue
        notification = Notification(user_id=user.id, **data)
        session.add(notification)
        created += 1

    return created


def seed_technician_tasks(
    session: Session,
    users: Dict[str, User],
) -> Tuple[Dict[str, TechnicianTask], int]:
    tasks_data = [
        (
            "urgent_visit",
            {
                "title": "زيارة صيانة عاجلة - التجمع الخامس",
                "description": "تنظيف سريع ومعالجة ماء قبل مناسبة عائلية.",
                "scheduled_date": date(2025, 1, 9),
                "scheduled_time": time(11, 0),
                "status": TechnicianTaskStatus.SCHEDULED,
                "priority": TaskPriority.URGENT,
                "location_name": "فيلا أحمد عبد الله",
                "location_address": "التجمع الخامس، شارع التسعين الشمالي",
                "location_latitude": 30.01,
                "location_longitude": 31.44,
                "customer_name": "أحمد عبد الله",
                "customer_phone": users["pool_owner"].phone,
                "notes": "يرغب العميل في التركيز على تنظيف الجاكوزي.",
            },
        ),
        (
            "weekly_plan",
            {
                "title": "صيانة باقة شهرية - الشيخ زايد",
                "description": "زيارة ثانية ضمن الباقة الشهرية مع قياس جودة المياه.",
                "scheduled_date": date(2025, 1, 12),
                "scheduled_time": time(13, 30),
                "status": TechnicianTaskStatus.IN_PROGRESS,
                "priority": TaskPriority.HIGH,
                "location_name": "فيلا دريم هيلز",
                "location_address": "الشيخ زايد، محور 26 يوليو",
                "location_latitude": 30.05,
                "location_longitude": 31.01,
                "customer_name": "مها فؤاد",
                "customer_phone": "+201000000333",
                "notes": "يرجى حمل مجموعة اختبار إضافية.",
            },
        ),
        (
            "indoor_assessment",
            {
                "title": "معاينة مسبح داخلي - مصر الجديدة",
                "description": "فحص المضخة والتأكد من نظام التهوية في المسبح المغلق.",
                "scheduled_date": date(2024, 12, 28),
                "scheduled_time": time(15, 0),
                "status": TechnicianTaskStatus.COMPLETED,
                "priority": TaskPriority.NORMAL,
                "location_name": "مجمع سكني - مصر الجديدة",
                "location_address": "مصر الجديدة، شارع الثورة",
                "location_latitude": 30.09,
                "location_longitude": 31.33,
                "customer_name": "شركة الريان",
                "customer_phone": "+201000000404",
                "completed_at": datetime(2024, 12, 28, 17, 0, tzinfo=timezone.utc),
                "notes": "تم الانتهاء وتثبيت تنبيه لمراجعة الفلاتر بعد شهر.",
            },
        ),
    ]

    technician = users["technician"]
    lookup: Dict[str, TechnicianTask] = {}
    created = 0

    for key, payload in tasks_data:
        data = payload.copy()
        filters = {
            "technician_id": technician.id,
            "title": data["title"],
            "scheduled_date": data["scheduled_date"],
        }
        existing = session.query(TechnicianTask).filter_by(**filters).first()
        if existing:
            lookup[key] = existing
            continue
        task = TechnicianTask(technician_id=technician.id, **data)
        session.add(task)
        session.flush()
        lookup[key] = task
        created += 1

    return lookup, created


def seed_pool_profiles(
    session: Session,
    tasks: Dict[str, TechnicianTask],
    pool_types: Dict[str, PoolType],
) -> int:
    profiles_data = [
        {
            "task_key": "urgent_visit",
            "pool_type_key": "family_pool",
            "nickname": "مسبح أحمد",
            "system_type": "Skimmer",
            "dimensions": "7m x 4m x 2m",
            "volume_liters": 56000,
            "notes": "يتم تغطية المسبح يومياً للحفاظ على نظافة المياه.",
        },
        {
            "task_key": "weekly_plan",
            "pool_type_key": "infinity_pool",
            "nickname": "فيلا الشيخ زايد",
            "system_type": "Overflow",
            "dimensions": "12m x 5m x 2.2m",
            "volume_liters": 120000,
            "notes": "نظام تحكم ذكي متصل بتطبيق محمول.",
        },
        {
            "task_key": "indoor_assessment",
            "pool_type_key": "indoor_pool",
            "nickname": "الصالة الداخلية",
            "system_type": "Heated",
            "dimensions": "6m x 3m x 1.6m",
            "volume_liters": 28800,
            "notes": "مزود بنظام إزالة رطوبة، يحتاج متابعة شهرية.",
        },
    ]

    created = 0

    for payload in profiles_data:
        data = payload.copy()
        task = tasks[data.pop("task_key")]
        pool_type = pool_types[data.pop("pool_type_key")]
        filters = {"task_id": task.id}
        existing = session.query(ClientPoolProfile).filter_by(**filters).first()
        if existing:
            continue
        profile = ClientPoolProfile(task_id=task.id, pool_type_id=pool_type.id, **data)
        session.add(profile)
        created += 1

    return created


def seed_water_quality(
    session: Session,
    tasks: Dict[str, TechnicianTask],
    technician: User,
) -> int:
    readings_data = [
        {
            "task_key": "urgent_visit",
            "recorded_at": datetime(2025, 1, 9, 12, 0, tzinfo=timezone.utc),
            "temperature_c": 26.5,
            "chlorine_ppm": 1.8,
            "ph_level": 7.3,
            "alkalinity_ppm": 110,
            "salinity_ppm": 0.0,
            "notes": "القيم ضمن المدى المثالي بعد المعالجة.",
        },
        {
            "task_key": "weekly_plan",
            "recorded_at": datetime(2025, 1, 12, 14, 15, tzinfo=timezone.utc),
            "temperature_c": 25.0,
            "chlorine_ppm": 2.2,
            "ph_level": 7.4,
            "alkalinity_ppm": 105,
            "salinity_ppm": 0.0,
            "notes": "تم إضافة كلور بسيط للحفاظ على الاتزان.",
        },
        {
            "task_key": "indoor_assessment",
            "recorded_at": datetime(2024, 12, 28, 16, 0, tzinfo=timezone.utc),
            "temperature_c": 28.0,
            "chlorine_ppm": 1.4,
            "ph_level": 7.2,
            "alkalinity_ppm": 115,
            "salinity_ppm": 0.0,
            "notes": "يجب تنظيف فلاتر التهوية في الزيارة القادمة.",
        },
    ]

    created = 0

    for payload in readings_data:
        data = payload.copy()
        task = tasks[data.pop("task_key")]
        filters = {
            "task_id": task.id,
            "recorded_at": data["recorded_at"],
        }
        existing = session.query(WaterQualityReading).filter_by(**filters).first()
        if existing:
            continue
        reading = WaterQualityReading(
            task_id=task.id,
            technician_id=technician.id,
            **data,
        )
        session.add(reading)
        created += 1

    return created


def seed_contact_messages(session: Session) -> int:
    messages_data = [
        {
            "name": "سارة منير",
            "email": "sara@example.com",
            "phone": "+201099998877",
            "message": "أرغب في تصميم مسبح للأطفال بعناصر أمان إضافية.",
            "status": "pending",
        },
        {
            "name": "عمر عبد السلام",
            "email": "omar@example.com",
            "phone": "+201066661212",
            "message": "هل يمكن إضافة نظام تدفئة لمسبح قائم؟",
            "status": "replied",
        },
    ]

    created = 0
    for payload in messages_data:
        filters = {"email": payload["email"], "message": payload["message"]}
        existing = session.query(ContactMessage).filter_by(**filters).first()
        if existing:
            continue
        contact_message = ContactMessage(**payload)
        session.add(contact_message)
        created += 1
    return created


def seed_faqs(session: Session) -> int:
    faqs_data = [
        {
            "question_ar": "ازاي أشوف المهام المطلوبة مني خلال الأسبوع؟",
            "question_en": "How do I see my required tasks for the week?",
            "answer_ar": "يمكنك عرض المهام المطلوبة منك من خلال قسم 'المهام' في التطبيق. ستجد قائمة بجميع المهام المجدولة مع تفاصيل كل مهمة مثل التاريخ والوقت والموقع.",
            "answer_en": "You can view your required tasks through the 'Tasks' section in the app. You'll find a list of all scheduled tasks with details like date, time, and location.",
            "category": "general",
            "sort_order": 1,
        },
        {
            "question_ar": "ازاي أتواصل مع الدعم؟",
            "question_en": "How do I contact support?",
            "answer_ar": "يمكنك التواصل مع فريق الدعم من خلال قسم 'مركز المساعدة' في حسابك. يمكنك إرسال رسالة مباشرة أو الاتصال بنا على الرقم المخصص للدعم.",
            "answer_en": "You can contact the support team through the 'Help Center' section in your account. You can send a direct message or call us on the dedicated support number.",
            "category": "general",
            "sort_order": 2,
        },
        {
            "question_ar": "ازاي أدخل على ملف كل عميل؟",
            "question_en": "How do I access each customer's profile?",
            "answer_ar": "يمكنك الوصول إلى ملف العميل من خلال قائمة المهام. اضغط على المهمة المخصصة للعميل وستجد رابط لملفه الشخصي مع جميع التفاصيل المهمة.",
            "answer_en": "You can access the customer's profile through the tasks list. Click on the task assigned to the customer and you'll find a link to their profile with all important details.",
            "category": "technical",
            "sort_order": 3,
        },
        {
            "question_ar": "فين بلاقي تاريخ مشترياتي؟",
            "question_en": "Where do I find my purchase history?",
            "answer_ar": "يمكنك العثور على تاريخ مشترياتك في قسم 'المتجر' ثم 'مشترياتي'. ستجد قائمة بجميع الطلبات السابقة مع تفاصيل كل طلب.",
            "answer_en": "You can find your purchase history in the 'Store' section then 'My Purchases'. You'll find a list of all previous orders with details of each order.",
            "category": "account",
            "sort_order": 4,
        },
        {
            "question_ar": "كيف أغير رقم الهاتف؟",
            "question_en": "How do I change my phone number?",
            "answer_ar": "يمكنك تغيير رقم الهاتف من خلال قسم 'معلومات الحساب' في حسابك. اضغط على زر التعديل بجانب رقم الهاتف وأدخل الرقم الجديد. سيتم إرسال رمز تحقق للرقم الجديد.",
            "answer_en": "You can change your phone number through the 'Account Information' section in your account. Click the edit button next to the phone number and enter the new number. A verification code will be sent to the new number.",
            "category": "account",
            "sort_order": 5,
        },
    ]

    created = 0
    for payload in faqs_data:
        filters = {"question_ar": payload["question_ar"]}
        existing = session.query(FAQ).filter_by(**filters).first()
        if existing:
            continue
        faq = FAQ(**payload)
        session.add(faq)
        created += 1
    return created


def seed_privacy_sections(session: Session) -> int:
    sections_data = [
        {
            "title_ar": "البيانات التي نجمعها",
            "title_en": "Data We Collect",
            "content_ar": "نجمع المعلومات الضرورية لتقديم خدماتنا بشكل فعال، بما في ذلك معلومات الحساب، بيانات الموقع، وسجل المهام والطلبات.",
            "content_en": "We collect necessary information to provide our services effectively, including account information, location data, and task and order history.",
            "sort_order": 1,
        },
        {
            "title_ar": "كيف نحمي معلوماتك؟",
            "title_en": "How Do We Protect Your Information?",
            "content_ar": "نستخدم تقنيات التشفير المتقدمة وحماية قوية للبيانات لضمان أمان معلوماتك. جميع البيانات محمية وفقاً لأعلى معايير الأمان.",
            "content_en": "We use advanced encryption technologies and strong data protection to ensure the security of your information. All data is protected according to the highest security standards.",
            "sort_order": 2,
        },
        {
            "title_ar": "عدم مشاركة البيانات",
            "title_en": "Do Not Share Data",
            "content_ar": "نحن لا نشارك بياناتك الشخصية مع أطراف ثالثة دون موافقتك الصريحة. بياناتك تبقى خاصة ومحمية.",
            "content_en": "We do not share your personal data with third parties without your explicit consent. Your data remains private and protected.",
            "sort_order": 3,
        },
        {
            "title_ar": "استخدام البيانات",
            "title_en": "Data Usage",
            "content_ar": "نستخدم بياناتك فقط لتحسين خدماتنا وتقديم تجربة أفضل لك. جميع المعلومات التي يتم جمعها تستخدم فقط لتقديم خدمات أفضل وتجربة أكثر دقة داخل التطبيق.",
            "content_en": "We use your data only to improve our services and provide you with a better experience. All collected information is used only to provide better services and a more accurate experience within the application.",
            "sort_order": 4,
        },
        {
            "title_ar": "التحكم الكامل في حسابك",
            "title_en": "Full Control Over Your Account",
            "content_ar": "لديك تحكم كامل في حسابك. يمكنك تحديث معلوماتك، حذف حسابك، أو طلب تصدير بياناتك في أي وقت.",
            "content_en": "You have full control over your account. You can update your information, delete your account, or request data export at any time.",
            "sort_order": 5,
        },
        {
            "title_ar": "التحديثات",
            "title_en": "Updates",
            "content_ar": "قد نقوم بتحديث سياسة الخصوصية من وقت لآخر. سنقوم بإعلامك بأي تغييرات مهمة عبر التطبيق.",
            "content_en": "We may update the privacy policy from time to time. We will notify you of any important changes through the app.",
            "sort_order": 6,
        },
    ]

    created = 0
    for payload in sections_data:
        filters = {"title_ar": payload["title_ar"]}
        existing = session.query(PrivacyPolicySection).filter_by(**filters).first()
        if existing:
            continue
        section = PrivacyPolicySection(**payload)
        session.add(section)
        created += 1
    return created


def seed_why_us_stats(session: Session) -> int:
    stats_data = [
        {
            "stat_type": "rating",
            "value": 4.8,
            "label_ar": "التقييم",
            "label_en": "Rating",
            "icon": "star",
        },
        {
            "stat_type": "experience_years",
            "value": 10.0,
            "label_ar": "سنوات خبرة",
            "label_en": "Years of Experience",
            "icon": "building",
        },
        {
            "stat_type": "completed_projects",
            "value": 500.0,
            "label_ar": "مشروع منجز",
            "label_en": "Completed Projects",
            "icon": "checkmark",
        },
    ]

    created = 0
    for payload in stats_data:
        filters = {"stat_type": payload["stat_type"]}
        existing = session.query(WhyUsStat).filter_by(**filters).first()
        if existing:
            continue
        stat = WhyUsStat(**payload)
        session.add(stat)
        created += 1
    return created


def seed_why_us_features(session: Session) -> int:
    features_data = [
        {
            "title_ar": "تنظيم المهام الأسبوعية",
            "title_en": "Weekly Task Organization",
            "description_ar": "نوفر لك جدول أعمال منظم يساعدك على إدارة وقتك بكفاءة وتلبية احتياجات العملاء في الوقت المحدد.",
            "description_en": "We provide you with an organized work schedule that helps you manage your time efficiently and meet customer needs on time.",
            "icon": "calendar",
            "sort_order": 1,
        },
        {
            "title_ar": "تقارير أداء شهرية",
            "title_en": "Monthly Performance Reports",
            "description_ar": "تحصل على تقارير شهرية مفصلة عن أدائك تساعدك على تحسين جودة خدماتك وزيادة دخلك.",
            "description_en": "You get detailed monthly reports on your performance that help you improve the quality of your services and increase your income.",
            "icon": "chart",
            "sort_order": 2,
        },
        {
            "title_ar": "دعم فني مستمر",
            "title_en": "Continuous Technical Support",
            "description_ar": "فريق دعم فني متاح على مدار الساعة لمساعدتك في أي استفسارات أو مشاكل تقنية تواجهها.",
            "description_en": "A technical support team available around the clock to assist you with any inquiries or technical issues you face.",
            "icon": "headset",
            "sort_order": 3,
        },
    ]

    created = 0
    for payload in features_data:
        filters = {"title_ar": payload["title_ar"]}
        existing = session.query(WhyUsFeature).filter_by(**filters).first()
        if existing:
            continue
        feature = WhyUsFeature(**payload)
        session.add(feature)
        created += 1
    return created


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("Creating tables (if needed)...")
    # Ensure all tables exist before seeding.
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        try:
            summary = {}

            users, created_users = seed_users(session)
            summary["users"] = created_users

            services, created_services = seed_services(session)
            summary["services"] = created_services

            pool_types, created_pool_types = seed_pool_types(session)
            summary["pool_types"] = created_pool_types

            packages, created_packages = seed_packages(session)
            summary["maintenance_packages"] = created_packages

            categories, created_categories = seed_categories(session)
            summary["categories"] = created_categories

            summary["products"] = seed_products(session, categories)
            summary["offers"] = seed_offers(session, services)

            bookings, created_bookings = seed_bookings(
                session,
                users,
                services,
                pool_types,
                packages,
            )
            summary["bookings"] = created_bookings

            summary["comments"] = seed_comments(session, users, bookings, services)
            summary["notifications"] = seed_notifications(session, users)

            tasks, created_tasks = seed_technician_tasks(session, users)
            summary["technician_tasks"] = created_tasks

            summary["pool_profiles"] = seed_pool_profiles(session, tasks, pool_types)
            summary["water_quality"] = seed_water_quality(
                session,
                tasks,
                users["technician"],
            )

            summary["contact_messages"] = seed_contact_messages(session)

            summary["faqs"] = seed_faqs(session)
            summary["privacy_sections"] = seed_privacy_sections(session)
            summary["why_us_stats"] = seed_why_us_stats(session)
            summary["why_us_features"] = seed_why_us_features(session)

            session.commit()
        except Exception as exc:  # pragma: no cover - utility script
            session.rollback()
            logger.exception("Seeding failed: %s", exc)
            raise

    logger.info("Seeding completed successfully:")
    for key, created in summary.items():
        logger.info("  - %-20s %s new records", key, created)


if __name__ == "__main__":
    main()