from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.schemas.medicion import MedicionOut
from app.crud import medicion as crud_medicion

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sensores/{sensor_id}/mediciones", response_model=list[MedicionOut])
def read_mediciones_by_sensor(sensor_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_medicion.get_mediciones_by_sensor(db, sensor_id=sensor_id, skip=skip, limit=limit)

@router.get("/sensores/{sensor_id}/mediciones/ultima", response_model=MedicionOut)
def read_ultima_medicion(sensor_id: int, db: Session = Depends(get_db)):
    medicion = crud_medicion.get_ultima_medicion_by_sensor(db, sensor_id=sensor_id)
    if medicion is None:
        raise HTTPException(status_code=404, detail="No hay mediciones para este sensor")
    return medicion