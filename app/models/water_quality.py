from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class WaterQualityReading(Base):
    """
    يخزن قراءات جودة المياه التي يقوم الفني بتحديثها أثناء الزيارة.
    """

    __tablename__ = "water_quality_readings"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        Integer,
        ForeignKey("technician_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    temperature_c = Column(Float, nullable=True)
    chlorine_ppm = Column(Float, nullable=True)
    ph_level = Column(Float, nullable=True)
    alkalinity_ppm = Column(Float, nullable=True)
    salinity_ppm = Column(Float, nullable=True)

    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    task = relationship("TechnicianTask", back_populates="water_quality_readings")
    technician = relationship("User")

