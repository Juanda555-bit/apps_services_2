from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import sensores, mediciones
from app.mqtt.cliente import mqtt_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client.start()
    yield
    mqtt_client.stop()

app = FastAPI(
    title="API IoT - Taller 2",
    description="API para gestión de sensores y mediciones MQTT",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(sensores.router, tags=["Sensores y Magnitudes"])
app.include_router(mediciones.router, tags=["Mediciones"])