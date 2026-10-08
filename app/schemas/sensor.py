from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SensorBase(BaseModel):
    codigo: str
    nombre: str
    categoria: str
    ubicacion: str
    activo: bool

class SensorOut(SensorBase):
    id: int
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)