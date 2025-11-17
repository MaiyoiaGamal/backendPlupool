from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WaterQualityReadingBase(BaseModel):
    temperature_c: Optional[float] = Field(
        None, description="درجة الحرارة بالسلزيوس"
    )
    chlorine_ppm: Optional[float] = Field(
        None, description="مستوى الكلور بالـ ppm"
    )
    ph_level: Optional[float] = Field(None, description="مستوى الحموضة PH")
    alkalinity_ppm: Optional[float] = Field(
        None, description="مستوى القلوية بالـ ppm"
    )
    salinity_ppm: Optional[float] = Field(
        None, description="مستوى الملوحة بالـ ppm"
    )
    notes: Optional[str] = Field(None, description="ملاحظات الزيارة")
    recorded_at: Optional[datetime] = Field(
        None, description="وقت تسجيل القراءة"
    )


class WaterQualityReadingCreate(WaterQualityReadingBase):
    pass


class WaterQualityReadingResponse(WaterQualityReadingBase):
    id: int
    task_id: int
    technician_id: Optional[int] = None
    recorded_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    relative_time: Optional[str] = None

    class Config:
        from_attributes = True


class WaterQualityHistoryResponse(BaseModel):
    latest: Optional[WaterQualityReadingResponse] = None
    history: list[WaterQualityReadingResponse] = Field(
        default_factory=list
    )
    ideal_ranges: dict[str, str]

