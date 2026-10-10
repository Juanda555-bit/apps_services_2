import logging
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud import sensor_magnitud as crud_sensor_magnitud
from app.database.connection import SessionLocal
from app.models.sensor_magnitud import SensorMagnitud
from app.schemas.sensor_magnitud import SensorMagnitudOut

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/sensores/{sensor_id}/magnitudes",
    response_model=list[SensorMagnitudOut],
)
def read_magnitudes_by_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
) -> list[SensorMagnitud]:
    try:
        magnitudes = crud_sensor_magnitud.get_magnitudes_by_sensor(
            db,
            sensor_id=sensor_id,
        )
    except SQLAlchemyError as error:
        logger.exception("Error consultando magnitudes del sensor %s", sensor_id)
        raise HTTPException(status_code=500, detail="Error consultando magnitudes") from error
    if not magnitudes:
        raise HTTPException(
            status_code=404,
            detail="Magnitudes no encontradas para este sensor",
        )
    return magnitudes


@router.get(
    "/sensor-magnitudes/{magnitud_id}",
    response_model=SensorMagnitudOut,
)
def read_sensor_magnitud(
    magnitud_id: int,
    db: Session = Depends(get_db),
) -> SensorMagnitud:
    try:
        sensor_magnitud = crud_sensor_magnitud.get_magnitud(
            db,
            magnitud_id=magnitud_id,
        )
    except SQLAlchemyError as error:
        logger.exception("Error consultando magnitud %s", magnitud_id)
        raise HTTPException(status_code=500, detail="Error consultando magnitud") from error
    if sensor_magnitud is None:
        raise HTTPException(status_code=404, detail="Magnitud no encontrada")
    return sensor_magnitud
