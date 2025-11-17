from datetime import date, time, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.technician_task import TechnicianTaskStatus, TaskPriority
from app.schemas.pool_profile import PoolProfileResponse
from app.schemas.water_quality import WaterQualityHistoryResponse


class TechnicianTaskBase(BaseModel):
    title: str = Field(..., description="عنوان المهمة")
    description: Optional[str] = Field(None, description="تفاصيل إضافية عن المهمة")
    scheduled_date: date = Field(..., description="تاريخ تنفيذ المهمة")
    scheduled_time: Optional[time] = Field(None, description="وقت تنفيذ المهمة")
    status: TechnicianTaskStatus = Field(default=TechnicianTaskStatus.SCHEDULED)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    location_name: Optional[str] = Field(None, description="اسم الموقع الظاهر")
    location_address: Optional[str] = Field(None, description="عنوان الموقع التفصيلي")
    location_latitude: Optional[float] = Field(None, description="احداثيات خط العرض")
    location_longitude: Optional[float] = Field(None, description="احداثيات خط الطول")
    customer_name: Optional[str] = Field(None, description="اسم العميل")
    customer_avatar: Optional[str] = Field(None, description="صورة العميل")
    customer_phone: Optional[str] = Field(None, description="رقم هاتف العميل")
    notes: Optional[str] = Field(None, description="ملاحظات داخلية")


class TechnicianTaskCreate(TechnicianTaskBase):
    technician_id: int = Field(..., description="معرف الفني")


class TechnicianTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    status: Optional[TechnicianTaskStatus] = None
    priority: Optional[TaskPriority] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    customer_name: Optional[str] = None
    customer_avatar: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    client_rating: Optional[int] = Field(None, ge=1, le=5, description="تقييم العميل بعد اكتمال المهمة")
    client_feedback: Optional[str] = None


class TechnicianTaskResponse(TechnicianTaskBase):
    id: int
    technician_id: int
    client_rating: Optional[int] = None
    client_feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TechnicianTaskListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    has_more: bool
    tasks: List[TechnicianTaskResponse]


class ClientDetailsSection(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    map_url: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    priority: TaskPriority = TaskPriority.NORMAL
    status: TechnicianTaskStatus = TechnicianTaskStatus.SCHEDULED


class TechnicianTaskDetailResponse(BaseModel):
    task: TechnicianTaskResponse
    client: ClientDetailsSection
    pool_profile: Optional[PoolProfileResponse] = None
    water_quality: WaterQualityHistoryResponse
        