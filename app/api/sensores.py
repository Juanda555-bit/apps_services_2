from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.schemas.medicion import SensorOut, SensorMagnitudOut
from app.crud import sensor as crud_sensor
from app.crud import sensor_magnitud as crud_magnitud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sensores", response_model=list[SensorOut])
def read_sensores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_sensor.get_sensores(db, skip=skip, limit=limit)

@router.get("/sensores/por-codigo/{codigo}", response_model=SensorOut)
def read_sensor_by_codigo(codigo: str, db: Session = Depends(get_db)):
    db_sensor = crud_sensor.get_sensor_by_codigo(db, codigo=codigo)
    if db_sensor is None:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return db_sensor

@router.get("/sensores/{sensor_id}", response_model=SensorOut)
def read_sensor(sensor_id: int, db: Session = Depends(get_db)):
    db_sensor = crud_sensor.get_sensor(db, sensor_id=sensor_id)
    if db_sensor is None:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return db_sensor

@router.get("/sensores/{sensor_id}/magnitudes", response_model=list[SensorMagnitudOut])
def read_magnitudes_by_sensor(sensor_id: int, db: Session = Depends(get_db)):
    magnitudes = crud_magnitud.get_magnitudes_by_sensor(db, sensor_id=sensor_id)
    if not magnitudes:
        raise HTTPException(status_code=404, detail="Magnitudes no encontradas para este sensor")
    return magnitudes