from pydantic import BaseModel, ConfigDict

class SensorMagnitudBase(BaseModel):
    magnitud: str
    unidad: str
    rango_min: float
    rango_max: float

class SensorMagnitudOut(SensorMagnitudBase):
    id: int
    sensor_id: int

    model_config = ConfigDict(from_attributes=True)