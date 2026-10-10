from datetime import datetime
from typing import Dict
from pydantic import BaseModel, ConfigDict

class SensorOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    categoria: str
    ubicacion: str
    activo: bool
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)

class SensorMagnitudOut(BaseModel):
    id: int
    sensor_id: int
    magnitud: str
    unidad: str
    valor_minimo: float
    valor_maximo: float

    model_config = ConfigDict(from_attributes=True)

class MedicionOut(BaseModel):
    id: int
    sensor_magnitud_id: int
    valor: float
    timestamp_utc: datetime

    model_config = ConfigDict(from_attributes=True)

class MeasurementValue(BaseModel):
    value: float
    unit: str

class PayloadMQTT(BaseModel):
    sensor_id: str
    timestamp: datetime
    measurements: Dict[str, MeasurementValue]