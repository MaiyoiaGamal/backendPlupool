from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ClientPoolProfile(Base):
    """
    يمثل بيانات مسبح العميل المرتبطة بمهمة فني محددة.
    يتم استخدامه لعرض تفاصيل المسبح (الحجم، الأبعاد، النوع) في شاشة الفني.
    """

    __tablename__ = "client_pool_profiles"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        Integer,
        ForeignKey("technician_tasks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    nickname = Column(String(255), nullable=True)
    pool_type_label = Column(String(255), nullable=True)
    pool_type_id = Column(Integer, ForeignKey("pool_types.id"), nullable=True)
    system_type = Column(String(255), nullable=True)  # Overflow / Skimmer ...

    volume_liters = Column(Float, nullable=True)
    dimensions = Column(String(255), nullable=True)  # مثل 12 × 6 × 1.8
    length_meters = Column(Float, nullable=True)
    width_meters = Column(Float, nullable=True)
    depth_meters = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    task = relationship(
        "TechnicianTask",
        back_populates="pool_profile",
    )
    pool_type = relationship("PoolType")

