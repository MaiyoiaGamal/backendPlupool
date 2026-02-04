from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    users,
    contact,
    notifications,
    service,
    booking,
    products,
    offers,
    dashboard,
    technician_tasks,
    cart,
    orders,
    search,
    account,
    admin,
    home,
)
api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
# Services routes (خدمات - أنواع المسابح - الباقات)
api_router.include_router (service.router,prefix="/service",tags=["الخدمات - Services"])
# Offers routes (عروض الخدمات - الإنشاء والصيانة) 
# متاحة لصاحب الحمام وممثل الشركة - تظهر في الصفحة الرئيسية
api_router.include_router(offers.router, prefix="/offers", tags=["عروض الخدمات - Service Offers (الإنشاء والصيانة)"])
# Bookings routes (الحجوزات)
api_router.include_router(booking.router, prefix="/booking", tags=["الحجوزات - Bookings"])
# Products routes (المنتجات - معدات الصيانة) 
# متاحة لجميع الأدوار - تظهر في المتجر للجميع، وفي الصفحة الرئيسية للفني فقط
api_router.include_router(products.router, prefix="/products", tags=["المنتجات - Products (معدات الصيانة)"])
# Cart routes (السلة)
api_router.include_router(cart.router, tags=["السلة - Cart"])
# Orders routes (الطلبات)
api_router.include_router(orders.router, tags=["الطلبات - Orders"])
# Search routes (البحث)
api_router.include_router(search.router, tags=["البحث - Search"])
# Account routes (حسابي)
api_router.include_router(account.router, tags=["حسابي - My Account"])
# Home routes (الصفحة الرئيسية - العروض والتعليقات)
api_router.include_router(home.router, prefix="/home", tags=["الصفحة الرئيسية - Home"])
# Dashboards per role
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboards"])
# Technician specific APIs
api_router.include_router(technician_tasks.router, prefix="/technician_tasks", tags=["Technician"])
# Admin APIs (للأدمن فقط - التحكم من الباك اند)
api_router.include_router(admin.router, tags=["Admin - إدارة النظام"])