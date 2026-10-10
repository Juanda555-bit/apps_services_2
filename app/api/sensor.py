import logging
from collections.abc import Generator
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud import sensor as crud_sensor
from app.database.connection import SessionLocal
from app.models.sensor import Sensor
from app.schemas.sensor import SensorOut

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/sensores", response_model=list[SensorOut])
def read_sensores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[Sensor]:
    try:
        return crud_sensor.get_sensores(db, skip=skip, limit=limit)
    except SQLAlchemyError as error:
        logger.exception("Error consultando sensores")
        raise HTTPException(status_code=500, detail="Error consultando sensores") from error


@router.get("/sensores/por-codigo/{codigo}", response_model=SensorOut)
def read_sensor_by_codigo(
    codigo: str,
    db: Session = Depends(get_db),
) -> Sensor:
    try:
        db_sensor = crud_sensor.get_sensor_by_codigo(db, codigo=codigo)
    except SQLAlchemyError as error:
        logger.exception("Error consultando sensor por código")
        raise HTTPException(status_code=500, detail="Error consultando sensor") from error
    if db_sensor is None:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return db_sensor


@router.get("/sensores/{sensor_id}", response_model=SensorOut)
def read_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
) -> Sensor:
    try:
        db_sensor = crud_sensor.get_sensor(db, sensor_id=sensor_id)
    except SQLAlchemyError as error:
        logger.exception("Error consultando sensor por identificador")
        raise HTTPException(status_code=500, detail="Error consultando sensor") from error
    if db_sensor is None:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return db_sensor
