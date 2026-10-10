from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import medicion, sensor, sensor_magnitud
from app.mqtt.cliente import mqtt_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        mqtt_client.start()
        yield
    finally:
        mqtt_client.stop()


app = FastAPI(
    title="API IoT - Taller 2",
    description="API para gestión de sensores y mediciones MQTT",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(sensor.router, tags=["Sensores"])
app.include_router(sensor_magnitud.router, tags=["Magnitudes"])
app.include_router(medicion.router, tags=["Mediciones"])