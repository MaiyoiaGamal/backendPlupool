from enum import Enum

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