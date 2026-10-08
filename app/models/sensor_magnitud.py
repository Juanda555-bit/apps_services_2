from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.sensor import Sensor
    from app.models.medicion import Medicion

class SensorMagnitud(Base):
    __tablename__ = "sensor_magnitudes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensores.id", ondelete="CASCADE"), nullable=False)
    magnitud: Mapped[str] = mapped_column(String(50), nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), nullable=False)
    rango_min: Mapped[float] = mapped_column(Float, nullable=False)
    rango_max: Mapped[float] = mapped_column(Float, nullable=False)

    sensor: Mapped["Sensor"] = relationship(back_populates="sensor_magnitudes")
    mediciones: Mapped[list["Medicion"]] = relationship(
        back_populates="sensor_magnitud",
        passive_deletes="all"
    )