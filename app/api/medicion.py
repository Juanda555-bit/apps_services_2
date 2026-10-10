import logging
from collections.abc import Generator
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud import medicion as crud_medicion
from app.database.connection import SessionLocal
from app.models.medicion import Medicion
from app.schemas.medicion import MedicionOut

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/sensores/{sensor_id}/mediciones", response_model=list[MedicionOut])
def read_mediciones_by_sensor(
    sensor_id: int,
    magnitud: Optional[str] = None,
    desde: Optional[AwareDatetime] = None,
    hasta: Optional[AwareDatetime] = None,
    limit: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
) -> list[Medicion]:
    if desde is not None and hasta is not None and desde > hasta:
        raise HTTPException(
            status_code=400,
            detail="La fecha 'desde' no puede ser posterior a 'hasta'",
        )

    try:
        return crud_medicion.get_mediciones_by_sensor(
            db,
            sensor_id=sensor_id,
            magnitud=magnitud,
            desde=desde,
            hasta=hasta,
            limit=limit,
        )
    except SQLAlchemyError as error:
        logger.exception("Error consultando mediciones del sensor %s", sensor_id)
        raise HTTPException(status_code=500, detail="Error consultando mediciones") from error


@router.get("/mediciones/{medicion_id}", response_model=MedicionOut)
def read_medicion(
    medicion_id: int,
    db: Session = Depends(get_db),
) -> Medicion:
    try:
        medicion = crud_medicion.get_medicion(db, medicion_id=medicion_id)
    except SQLAlchemyError as error:
        logger.exception("Error consultando medición %s", medicion_id)
        raise HTTPException(status_code=500, detail="Error consultando medición") from error
    if medicion is None:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    return medicion


@router.get("/sensores/{sensor_id}/ultima-medicion", response_model=MedicionOut)
@router.get("/sensores/{sensor_id}/mediciones/ultima", response_model=MedicionOut)
def read_ultima_medicion(
    sensor_id: int,
    db: Session = Depends(get_db),
) -> Medicion:
    try:
        medicion = crud_medicion.get_ultima_medicion(db, sensor_id=sensor_id)
    except SQLAlchemyError as error:
        logger.exception("Error consultando última medición del sensor %s", sensor_id)
        raise HTTPException(status_code=500, detail="Error consultando medición") from error
    if medicion is None:
        raise HTTPException(status_code=404, detail="No hay mediciones para este sensor")
    return medicion