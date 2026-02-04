from datetime import datetime, timedelta
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.service_offer import OfferStatus, ServiceOffer
from app.schemas.service_offer import ServiceOfferDetailResponse
from app.models.comment import Comment
from app.models.user import User
from app.models.enums import UserRole, BookingType, BookingStatus
from app.models.booking import Booking
from app.models.product import Product, ProductStatus
from app.schemas.product import ProductDetailResponse
from app.schemas.comment import CommentCreate, CommentResponse, CommentsListResponse
from app.schemas.account import ProjectResponse
from app.core.dependencies import get_current_active_user, get_current_user_optional


def _summary_with_role(base: str, role_label: Optional[str]) -> str:
    return f"{base} - {role_label}" if role_label else base


def _fetch_featured_service_offers(limit: int, db: Session) -> List[ServiceOfferDetailResponse]:
    """
    جلب عروض الخدمات (للإنشاء والصيانة) - لصاحب الحمام وممثل الشركة
    Fetch service offers (construction & maintenance) - for Pool Owner and Company
    """
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


def _fetch_featured_products(limit: int, db: Session) -> List[ProductDetailResponse]:
    """
    جلب المنتجات المميزة من المتجر - للفني
    Fetch featured products from store - for Technician
    """
    products = (
        db.query(Product)
        .filter(
            Product.is_featured == True,
            Product.status == ProductStatus.ACTIVE,
        )
        .order_by(
            desc(Product.sort_order) if hasattr(Product, 'sort_order') else desc(Product.created_at),
            desc(Product.created_at),
        )
        .limit(limit)
        .all()
    )

    results: List[ProductDetailResponse] = []
    for product in products:
        product_dict = ProductDetailResponse(**product.__dict__)
        if product.category:
            product_dict.category_name = product.category.name_ar
        results.append(product_dict)

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


def _relative_time(created_at: datetime) -> str:
    """
    حساب الوقت النسبي (مثل "منذ ساعتين")
    Calculate relative time (e.g., "منذ ساعتين")
    """
    now = datetime.now()
    if created_at.tzinfo:
        now = datetime.now(created_at.tzinfo)
    
    diff = now - created_at
    
    if diff.days > 365:
        years = diff.days // 365
        return f"منذ {years} {'سنة' if years == 1 else 'سنوات'}"
    elif diff.days > 30:
        months = diff.days // 30
        return f"منذ {months} {'شهر' if months == 1 else 'أشهر'}"
    elif diff.days > 0:
        return f"منذ {diff.days} {'يوم' if diff.days == 1 else 'أيام'}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"منذ {hours} {'ساعة' if hours == 1 else 'ساعات'}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"منذ {minutes} {'دقيقة' if minutes == 1 else 'دقائق'}"
    else:
        return "الآن"


def create_home_router(role_label: Optional[str] = None) -> APIRouter:
    home_router = APIRouter()

    @home_router.get(
        "/featured-offers",
        response_model=Union[List[ServiceOfferDetailResponse], List[ProductDetailResponse]],
        summary=_summary_with_role("العروض المميزة للصفحة الرئيسية (Home Page)", role_label),
    )
    def get_featured_offers(
        limit: int = 6,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user_optional),
    ):
        """
        الحصول على العروض المميزة للصفحة الرئيسية حسب دور المستخدم:
        
        **للفني (Technician):**
        - يعرض: المنتجات المميزة من المتجر (معدات الصيانة)
        - النوع: منتجات (Products) - مضخات، فلاتر، معدات
        - متاحة في: المتجر للجميع، الصفحة الرئيسية للفني فقط
        - عند الضغط على "عرض الكل": يفتح صفحة المتجر (/products)
        - استخدم: /products/featured للحصول على نفس النتيجة
        
        **لصاحب الحمام (Pool Owner) وممثل الشركة (Company):**
        - يعرض: عروض الخدمات (الإنشاء والصيانة)
        - النوع: عروض الخدمات (Service Offers) - إنشاء، صيانة، تركيب أنظمة
        - متاحة لـ: صاحب الحمام وممثل الشركة فقط
        - تظهر في: الصفحة الرئيسية فقط
        - عند الضغط على "عرض الكل": يفتح صفحة عروض الخدمات (/offers)
        - استخدم: /offers/featured للحصول على نفس النتيجة
        
        **بدون تسجيل دخول:**
        - يعرض: عروض الخدمات (افتراضي)
        
        **ملاحظات مهمة:**
        - هذا الـ endpoint مخصص للصفحة الرئيسية فقط
        - المنتجات (Products) متاحة للجميع في المتجر
        - عروض الخدمات (Service Offers) خاصة بصاحب الحمام وممثل الشركة
        """
        # إذا كان المستخدم فني، نعرض المنتجات
        if current_user and current_user.role == UserRole.TECHNICIAN:
            return _fetch_featured_products(limit, db)
        else:
            # لصاحب الحمام وممثل الشركة والزوار: نعرض عروض الخدمات
            return _fetch_featured_service_offers(limit, db)

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

    # ============= Projects Section (مشاريعنا) =============
    # هذه المشاريع تظهر لجميع الأدوار في الصفحة الرئيسية
    
    @home_router.get(
        "/projects",
        response_model=List[ProjectResponse],
        summary=_summary_with_role("مشاريعنا - المشاريع المميزة", role_label),
    )
    def get_featured_projects(
        limit: int = 6,
        db: Session = Depends(get_db),
    ):
        """
        الحصول على المشاريع المميزة (مشاريع إنشاء المسابح)
        
        **متاح لـ:** جميع الأدوار (كل المستخدمين)
        **يظهر في:** الصفحة الرئيسية (Home Page) لجميع الأدوار
        
        هذه المشاريع خاصة بـ:
        - إنشاء المسابح
        - مشاريع الإنشاء المكتملة أو قيد التنفيذ
        - تعرض كأمثلة على أعمال الشركة
        """
        # جلب الحجوزات من نوع إنشاء مسبح (مشاريع)
        # نعرض المشاريع المكتملة أو قيد التنفيذ فقط
        bookings = (
            db.query(Booking)
            .filter(
                Booking.booking_type == BookingType.CONSTRUCTION,
                Booking.status.in_([BookingStatus.IN_PROGRESS, BookingStatus.COMPLETED])
            )
            .order_by(Booking.created_at.desc())
            .limit(limit)
            .all()
        )
        
        projects = []
        for booking in bookings:
            # استخراج اسم المشروع
            project_name = None
            if booking.pool_type:
                project_name = booking.pool_type.name_ar
            elif booking.admin_notes:
                # إذا كان فيه admin_notes، نستخدمه كاسم المشروع
                project_name = booking.admin_notes.split('\n')[0] if '\n' in booking.admin_notes else booking.admin_notes
            else:
                project_name = "مشروع إنشاء مسبح"
            
            # استخراج الوصف من admin_notes أو استخدام وصف افتراضي
            description = None
            if booking.admin_notes and '\n' in booking.admin_notes:
                description = '\n'.join(booking.admin_notes.split('\n')[1:])
            elif booking.admin_notes:
                description = booking.admin_notes
            else:
                description = "تصميم فاخر مع ضمان 10 سنوات وصيانة مجانية لمدة 3 شهور"
            
            # صورة المشروع
            project_image = booking.project_image if booking.project_image else None
            
            # حساب نسبة الإنجاز
            completion_percentage = 100.0 if booking.status == BookingStatus.COMPLETED else 50.0
            
            # الموقع
            location = booking.user.address if booking.user else None
            
            # تاريخ البدء والانتهاء
            start_date = str(booking.booking_date) if booking.booking_date else None
            end_date = str(booking.next_maintenance_date) if booking.next_maintenance_date else None
            
            projects.append(
                ProjectResponse(
                    booking_id=booking.id,
                    project_name=project_name,
                    location=location,
                    pools_count=1,  # افتراضي - يمكن تحسينه لاحقاً
                    completion_percentage=completion_percentage,
                    status=booking.status.value,
                    start_date=start_date,
                    end_date=end_date,
                    next_visit=None,  # للصفحة الرئيسية مش محتاجين next_visit
                    image_url=project_image,  # صورة المشروع
                )
            )
        
        return projects

    # ============= Comments/Reviews Section =============
    # هذه التعليقات خاصة بصاحب الحمام وممثل الشركة فقط (ليس للفني)
    
    @home_router.post(
        "/comments",
        response_model=CommentResponse,
        status_code=status.HTTP_201_CREATED,
        summary=_summary_with_role("إضافة تعليق/تقييم", role_label),
    )
    def create_comment(
        comment_data: CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ):
        """
        إضافة تعليق/تقييم جديد
        
        **متاح لـ:** صاحب الحمام وممثل الشركة فقط (ليس للفني)
        
        - يمكن ربطه بخدمة معينة (service_id)
        - أو بحجز معين (booking_id)
        - أو يكون تعليق عام بدون ربط
        """
        # التحقق من الدور - الفني غير مسموح له
        if current_user.role == UserRole.TECHNICIAN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="هذه الميزة متاحة لصاحب الحمام وممثل الشركة فقط"
            )
        # التحقق من صحة التقييم
        if comment_data.rating < 1 or comment_data.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="التقييم يجب أن يكون بين 1 و 5"
            )
        
        # التحقق من وجود service_id إذا تم إرساله
        if comment_data.service_id:
            from app.models.service import Service
            service = db.query(Service).filter(Service.id == comment_data.service_id).first()
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="الخدمة غير موجودة"
                )
        
        # التحقق من وجود booking_id إذا تم إرساله
        if comment_data.booking_id:
            from app.models.booking import Booking
            booking = db.query(Booking).filter(Booking.id == comment_data.booking_id).first()
            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="الحجز غير موجود"
                )
        
        # إنشاء التعليق
        new_comment = Comment(
            user_id=current_user.id,
            content=comment_data.content,
            rating=comment_data.rating,
            service_id=comment_data.service_id,
            booking_id=comment_data.booking_id,
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # إرجاع التعليق مع معلومات المستخدم
        return CommentResponse(
            id=new_comment.id,
            user_id=new_comment.user_id,
            user_name=current_user.full_name or "مستخدم Plupool",
            user_avatar=current_user.profile_image,
            content=new_comment.content,
            rating=new_comment.rating,
            service_id=new_comment.service_id,
            booking_id=new_comment.booking_id,
            created_at=new_comment.created_at,
            relative_time=_relative_time(new_comment.created_at),
        )
    
    @home_router.get(
        "/comments",
        response_model=CommentsListResponse,
        summary=_summary_with_role("عرض التعليقات والتقييمات", role_label),
    )
    def get_comments(
        service_id: Optional[int] = None,
        booking_id: Optional[int] = None,
        sort_by: str = "all",  # all, newest, oldest, highest_rating, lowest_rating
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user_optional),
    ):
        """
        الحصول على قائمة التعليقات والتقييمات
        
        **متاح لـ:** صاحب الحمام وممثل الشركة فقط (ليس للفني)
        **الفني:** غير مسموح له بعرض التعليقات تماماً (حتى بدون تسجيل دخول)
        **بدون تسجيل دخول:** يمكن عرض التعليقات (قراءة فقط)
        
        - يمكن فلترة حسب service_id أو booking_id
        - أو عرض جميع التعليقات العامة
        - خيارات الترتيب:
          * "all" - الكل (الأحدث أولاً - افتراضي)
          * "newest" - الأحدث
          * "oldest" - الأقدم
          * "highest_rating" - الأعلى تقييماً
          * "lowest_rating" - الأقل تقييماً
        """
        # التحقق من الدور - الفني غير مسموح له تماماً
        if current_user and current_user.role == UserRole.TECHNICIAN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="هذه الميزة متاحة لصاحب الحمام وممثل الشركة فقط. الفني غير مسموح له بعرض التعليقات"
            )
        query = db.query(Comment).join(User, Comment.user_id == User.id)
        
        # فلترة حسب service_id
        if service_id:
            query = query.filter(Comment.service_id == service_id)
        
        # فلترة حسب booking_id
        if booking_id:
            query = query.filter(Comment.booking_id == booking_id)
        
        # إذا لم يتم تحديد service_id أو booking_id، عرض التعليقات العامة فقط
        if not service_id and not booking_id:
            query = query.filter(
                Comment.service_id.is_(None),
                Comment.booking_id.is_(None)
            )
        
        # حساب المتوسط
        avg_rating = query.with_entities(func.avg(Comment.rating)).scalar()
        average_rating = round(float(avg_rating), 1) if avg_rating else None
        
        # الحصول على العدد الإجمالي
        total = query.count()
        
        # الترتيب حسب الخيار المحدد
        if sort_by == "newest" or sort_by == "all":
            # الأحدث أولاً (افتراضي)
            comments = query.order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()
        elif sort_by == "oldest":
            # الأقدم أولاً
            comments = query.order_by(Comment.created_at).offset(skip).limit(limit).all()
        elif sort_by == "highest_rating":
            # الأعلى تقييماً أولاً
            comments = query.order_by(desc(Comment.rating), desc(Comment.created_at)).offset(skip).limit(limit).all()
        elif sort_by == "lowest_rating":
            # الأقل تقييماً أولاً
            comments = query.order_by(Comment.rating, desc(Comment.created_at)).offset(skip).limit(limit).all()
        else:
            # افتراضي: الأحدث أولاً
            comments = query.order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()
        
        # تحويل إلى response
        comments_list = []
        for comment in comments:
            comments_list.append(
                CommentResponse(
                    id=comment.id,
                    user_id=comment.user_id,
                    user_name=comment.user.full_name if comment.user else "مستخدم Plupool",
                    user_avatar=comment.user.profile_image if comment.user else None,
                    content=comment.content,
                    rating=comment.rating,
                    service_id=comment.service_id,
                    booking_id=comment.booking_id,
                    created_at=comment.created_at,
                    relative_time=_relative_time(comment.created_at),
                )
            )
        
        return CommentsListResponse(
            comments=comments_list,
            total=total,
            average_rating=average_rating,
            sort_by=sort_by,
        )

    return home_router


router = create_home_router()


__all__ = [
    "router",
    "create_home_router",
    "_fetch_featured_service_offers",
    "_fetch_featured_products",
    "_fetch_home_stats",
]