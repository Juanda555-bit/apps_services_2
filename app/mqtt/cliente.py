import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from paho.mqtt.client import MQTTMessage
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.sensor import get_sensor_by_codigo
from app.crud.sensor_magnitud import get_magnitudes_by_sensor
from app.database.connection import SessionLocal
from app.models.medicion import Medicion
from app.schemas.medicion import PayloadMQTT

load_dotenv()

logger = logging.getLogger(__name__)

class MQTTConsumer:
    def __init__(self) -> None:
        self._broker = os.getenv("MQTT_BROKER", "").strip()
        self._port = int(os.getenv("MQTT_PORT", "1883"))
        self._topic = os.getenv("MQTT_TOPIC", "iot/sensors/TEST-001/data").strip()
        self._username = os.getenv("MQTT_USERNAME", "").strip()
        self._password = os.getenv("MQTT_PASSWORD", "").strip()
        self._keepalive = int(os.getenv("MQTT_KEEPALIVE", "60"))
        self._started = False
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if self._username:
            self._client.username_pw_set(self._username, self._password)

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def start(self) -> None:
        if not self._broker:
            raise RuntimeError("Falta configurar MQTT_BROKER en el archivo .env")

        self._client.connect(self._broker, self._port, self._keepalive)
        self._client.loop_start()
        self._started = True
        logger.info("Cliente MQTT iniciado para el tópico %s", self._topic)

    def stop(self) -> None:
        if not self._started:
            return

        try:
            self._client.disconnect()
        finally:
            self._client.loop_stop()
            self._started = False
        logger.info("Cliente MQTT detenido")

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        if reason_code != 0:
            logger.error("No se pudo conectar al broker MQTT: %s", reason_code)
            return

        result, _ = client.subscribe(self._topic)
        if result != mqtt.MQTT_ERR_SUCCESS:
            logger.error(
                "No fue posible suscribirse al tópico %s: código %s",
                self._topic,
                result,
            )
            return

        logger.info("Suscrito al tópico MQTT %s", self._topic)

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        message: MQTTMessage,
    ) -> None:
        try:
            payload = PayloadMQTT.model_validate_json(message.payload)
        except ValidationError as error:
            logger.warning("Payload MQTT inválido en %s: %s", message.topic, error)
            return

        if payload.timestamp.tzinfo is None or payload.timestamp.utcoffset() is None:
            logger.warning("Timestamp MQTT sin zona horaria en %s", message.topic)
            return
        if not payload.measurements:
            logger.warning("Payload MQTT sin mediciones en %s", message.topic)
            return

        timestamp_utc = payload.timestamp.astimezone(timezone.utc)
        db: Session | None = None
        try:
            db = SessionLocal()
            sensor = get_sensor_by_codigo(db, payload.sensor_id)
            if sensor is None or not sensor.activo:
                logger.warning(
                    "Sensor inexistente o inactivo en mensaje MQTT: %s",
                    payload.sensor_id,
                )
                return

            sensor_magnitudes = get_magnitudes_by_sensor(db, sensor.id)
            magnitudes = {item.magnitud: item for item in sensor_magnitudes}
            pending: list[Medicion] = []

            for name, measurement in payload.measurements.items():
                sensor_magnitud = magnitudes.get(name)
                if sensor_magnitud is None:
                    logger.warning("Magnitud %s no configurada para el sensor", name)
                    return
                if measurement.unit != sensor_magnitud.unidad:
                    logger.warning("Unidad incorrecta para la magnitud %s", name)
                    return

                value = Decimal(str(measurement.value))
                if not value.is_finite():
                    logger.warning("Valor no finito para la magnitud %s", name)
                    return
                if not (
                    Decimal(str(sensor_magnitud.valor_minimo))
                    <= value
                    <= Decimal(str(sensor_magnitud.valor_maximo))
                ):
                    logger.warning("Valor fuera de rango para la magnitud %s", name)
                    return

                pending.append(
                    Medicion(
                        sensor_magnitud_id=sensor_magnitud.id,
                        valor=value,
                        timestamp_utc=timestamp_utc,
                    )
                )

            db.add_all(pending)
            db.commit()
            logger.info(
                "Almacenadas %s mediciones válidas del sensor %s",
                len(pending),
                payload.sensor_id,
            )
        except SQLAlchemyError:
            if db is not None:
                try:
                    db.rollback()
                except SQLAlchemyError:
                    logger.exception(
                        "Error revirtiendo transacción MQTT del sensor %s",
                        payload.sensor_id,
                    )
            logger.exception(
                "Error de base de datos procesando mensaje MQTT del sensor %s",
                payload.sensor_id,
            )
        finally:
            if db is not None:
                try:
                    db.close()
                except SQLAlchemyError:
                    logger.exception(
                        "Error cerrando sesión de base de datos del sensor %s",
                        payload.sensor_id,
                    )

mqtt_client = MQTTConsumer()