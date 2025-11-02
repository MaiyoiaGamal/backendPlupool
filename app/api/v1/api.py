from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    booking,
    company,
    contact,
    health,
    notifications,
    offers,
    pool_owner,
    products,
    service,
    suggestions,
    technician,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["Suggestions"])
# Services routes (خدمات - أنواع المسابح - الباقات)
api_router.include_router (service.router,prefix="/service",tags=["الخدمات - Services"])
# Offers routes ( العروض علي الخدمات) 
api_router.include_router(offers.router,prefix="/offers",tags=["العروض - Offers"])
# Bookings routes (الحجوزات)
api_router.include_router(booking.router,prefix="/booking",tags=["الحجوزات - Bookings"])
# Products routes (المنتجات والعروض) 
api_router.include_router(products.router,prefix="/products",tags=["المنتجات والعروض - Products & Offers"])
 # Role-based portals
api_router.include_router(pool_owner.router, prefix="/pool-owner")
api_router.include_router(company.router, prefix="/company")
api_router.include_router(technician.router, prefix="/technician")
