from datetime import datetime, timedelta, timezone

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    StrictFloat,
    StrictStr,
    computed_field,
    field_validator,
)

COLOMBIA_TIMEZONE = timezone(timedelta(hours=-5))


class MedicionOut(BaseModel):
    id: int
    sensor_magnitud_id: int
    valor: float
    timestamp_utc: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("timestamp_utc")
    @classmethod
    def normalize_timestamp_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp_utc debe incluir información de zona horaria")
        return value.astimezone(timezone.utc)

    @computed_field(return_type=str)
    @property
    def timestamp_local(self) -> str:
        return self.timestamp_utc.astimezone(COLOMBIA_TIMEZONE).isoformat(
            timespec="seconds"
        )


class MeasurementValue(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    value: StrictFloat
    unit: StrictStr


class PayloadMQTT(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    sensor_id: StrictStr
    timestamp: AwareDatetime
    measurements: dict[str, MeasurementValue]