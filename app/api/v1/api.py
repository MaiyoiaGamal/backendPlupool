from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, users, contact, notifications, suggestions ,service , booking , products ,offers, home

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["Suggestions"])
# Home routes (الصفحة الرئيسية المخصصة)
api_router.include_router(home.router, prefix="/home", tags=["الصفحة الرئيسية - Home"])
# Services routes (خدمات - أنواع المسابح - الباقات)
api_router.include_router (service.router,prefix="/service",tags=["الخدمات - Services"])
# Offers routes ( العروض علي الخدمات) 
api_router.include_router(offers.router,prefix="/offers",tags=["العروض - Offers"])
# Bookings routes (الحجوزات)
api_router.include_router(booking.router,prefix="/booking",tags=["الحجوزات - Bookings"])
# Products routes (المنتجات والعروض) 
api_router.include_router(products.router,prefix="/products",tags=["المنتجات والعروض - Products & Offers"])
