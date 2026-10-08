from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.sensor_magnitud import SensorMagnitud

class Medicion(Base):
    __tablename__ = "mediciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_magnitud_id: Mapped[int] = mapped_column(ForeignKey("sensor_magnitudes.id", ondelete="CASCADE"), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    sensor_magnitud: Mapped["SensorMagnitud"] = relationship(back_populates="mediciones")