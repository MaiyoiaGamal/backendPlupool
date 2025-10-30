# app/models/enums.py
from enum import Enum


class UserRole(str, Enum):
    GUEST = "guest"             # ضيف - Browse only
    POOL_OWNER = "pool_owner"   # صاحب حمام
    TECHNICIAN = "technician"   # فني صيانة
    COMPANY = "company"         # شركة 

class BookingType(str, Enum):
    CONSTRUCTION = "construction"
    MAINTENANCE_SINGLE = "maintenance_single"
    MAINTENANCE_PACKAGE = "maintenance_package"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

