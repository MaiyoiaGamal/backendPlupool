from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PoolProfileBase(BaseModel):
    nickname: Optional[str] = None
    pool_type_label: Optional[str] = None
    pool_type_id: Optional[int] = None
    system_type: Optional[str] = None
    volume_liters: Optional[float] = None
    dimensions: Optional[str] = None
    length_meters: Optional[float] = None
    width_meters: Optional[float] = None
    depth_meters: Optional[float] = None
    notes: Optional[str] = None


class PoolProfileResponse(PoolProfileBase):
    id: int
    task_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
