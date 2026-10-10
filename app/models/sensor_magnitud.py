from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.sensor import Sensor
    from app.models.medicion import Medicion


class SensorMagnitud(Base):
    __tablename__ = "sensor_magnitudes"
    __table_args__ = (
        UniqueConstraint("sensor_id", "magnitud"),
        CheckConstraint("valor_minimo < valor_maximo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sensores.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    magnitud: Mapped[str] = mapped_column(String(50), nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), nullable=False)
    valor_minimo: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    valor_maximo: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    sensor: Mapped["Sensor"] = relationship(back_populates="sensor_magnitudes")
    mediciones: Mapped[list["Medicion"]] = relationship(
        back_populates="sensor_magnitud",
        passive_deletes="all",
    )