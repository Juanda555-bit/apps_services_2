from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional

from app.models.medicion import Medicion
from app.models.sensor_magnitud import SensorMagnitud

def create_medicion(db: Session, sensor_magnitud_id: int, valor: float, timestamp_utc: datetime):
    db_medicion = Medicion(
        sensor_magnitud_id=sensor_magnitud_id,
        valor=valor,
        timestamp_utc=timestamp_utc
    )
    db.add(db_medicion)
    db.commit()
    db.refresh(db_medicion)
    return db_medicion

def get_medicion(db: Session, medicion_id: int):
    return db.query(Medicion).filter(Medicion.id == medicion_id).first()

def get_ultima_medicion(db: Session, sensor_id: int):
    return (
        db.query(Medicion)
        .join(SensorMagnitud)
        .filter(SensorMagnitud.sensor_id == sensor_id)
        .order_by(desc(Medicion.timestamp_utc))
        .first()
    )

def get_mediciones_by_sensor(
    db: Session, 
    sensor_id: int, 
    magnitud: Optional[str] = None, 
    desde: Optional[datetime] = None, 
    hasta: Optional[datetime] = None, 
    limit: Optional[int] = None
):
    query = db.query(Medicion).join(SensorMagnitud).filter(SensorMagnitud.sensor_id == sensor_id)
    
    if magnitud:
        query = query.filter(SensorMagnitud.magnitud == magnitud)
    if desde:
        query = query.filter(Medicion.timestamp_utc >= desde)
    if hasta:
        query = query.filter(Medicion.timestamp_utc <= hasta)
        
    query = query.order_by(desc(Medicion.timestamp_utc))
    
    if limit:
        query = query.limit(limit)
        
    return query.all()