from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict

class MedicionBase(BaseModel):
    valor: float

class MedicionOut(MedicionBase):
    id: int
    sensor_magnitud_id: int
    timestamp_utc: datetime

    model_config = ConfigDict(from_attributes=True)

class MeasurementItem(BaseModel):
    value: float
    unit: str

class PayloadMQTT(BaseModel):
    sensor_id: str
    timestamp: datetime
    measurements: Dict[str, MeasurementItem]