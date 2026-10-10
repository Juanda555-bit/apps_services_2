from pydantic import BaseModel, ConfigDict


class SensorMagnitudBase(BaseModel):
    magnitud: str
    unidad: str
    valor_minimo: float
    valor_maximo: float


class SensorMagnitudOut(SensorMagnitudBase):
    id: int
    sensor_id: int

    model_config = ConfigDict(from_attributes=True)