# Evidencias de validación

Fecha de ejecución: 10 de octubre de 2026.

## Captura MQTT y persistencia en PostgreSQL

La API/consumidor se inició a las 18:02:46 (hora de Colombia) y se mantuvo
activo hasta después de las 18:25:51. Para el sensor configurado en el tópico
se contó un baseline de 1.722 filas a las 18:05:15 y 2.192 filas a las
18:25:51: un aumento neto de 470 registros de medición durante más de 20
minutos. El timestamp más reciente estaba a menos de seis segundos de la
consulta final.

El payload almacenado más reciente observado fue reconstruido al agrupar las
filas de `mediciones` que compartían `timestamp_utc`:

```json
{
  "sensor_id": "GAS-001",
  "timestamp": "2026-10-10T23:25:46Z",
  "measurements": {
    "co": {
      "value": 14.29,
      "unit": "ppm"
    },
    "temperature": {
      "value": 22.17,
      "unit": "C"
    }
  }
}
```

El tópico observado fue `iot/sensors/GAS-001/data`. La aplicación no conserva
el mensaje MQTT original como texto; la muestra se deriva de los registros
persistidos.

## Pruebas HTTP

Las solicitudes se hicieron contra la aplicación local conectada a PostgreSQL.

| Caso | Solicitud/entrada | Resultado | Código |
|---|---|---|---:|
| Listado de sensores | `GET /sensores?limit=1` | Respuesta exitosa. | 200 |
| Sensor por ID | `GET /sensores/4` | Sensor existente retornado. | 200 |
| Sensor por código | `GET /sensores/por-codigo/GAS-001` | Sensor existente retornado. | 200 |
| Magnitudes del sensor | `GET /sensores/4/magnitudes` | Magnitudes retornadas. | 200 |
| Magnitud por ID | `GET /sensor-magnitudes/11` | Magnitud existente retornada. | 200 |
| Medición por ID | `GET /mediciones/120511` | Medición existente retornada. | 200 |
| Histórico | `GET /sensores/4/mediciones?magnitud=temperature&desde=2000-01-01T00:00:00Z&hasta=2100-01-01T00:00:00Z&limit=10` | Diez resultados o menos, del más reciente al más antiguo; respuesta con `timestamp_local`. | 200 |
| Rango y magnitud | Ventana de diez minutos alrededor de la última medición y magnitud configurada. | Registros dentro del intervalo y asociados a la magnitud solicitada. | 200 |
| Última medición | `GET /sensores/4/ultima-medicion` | Última medición retornada. | 200 |
| Rango invertido | `desde=2026-10-10T10:00:00Z`, `hasta=2026-10-09T10:00:00Z` | Rango rechazado. | 400 |
| ID inexistente | `GET /mediciones/9223372036854775807` | Medición no encontrada. | 404 |
| Límite inválido | `GET /sensores/1/mediciones?limit=0` | Parámetro rechazado. | 422 |
| Fecha sin zona horaria | `GET /sensores/1/mediciones?desde=2026-10-07T16:25:30` | Parámetro rechazado. | 422 |

Archivos relacionados: `app/api/sensor.py`,
`app/api/sensor_magnitud.py`, `app/api/medicion.py`,
`app/crud/medicion.py` y `app/schemas/medicion.py`.

## Payloads MQTT inválidos

Durante la ventana de recepción se observaron registros `logger.warning` en
`app/mqtt/cliente.py` para timestamp no parseable, tipo numérico incorrecto,
campos internos faltantes, unidades incorrectas, valor fuera de rango y
magnitudes no configuradas. La ruta de callback es
`MQTTConsumer._on_message`.

Extractos representativos de los registros observados:

```text
Unidad incorrecta para la magnitud co
Valor fuera de rango para la magnitud temperature
Payload MQTT inválido ... timestamp: Input should be a valid datetime
Payload MQTT inválido ... measurements.co.value: Input should be a valid number
Payload MQTT inválido ... measurements.temperature.unit: Field required
Magnitud humidity no configurada para el sensor
```

Además, se ejecutaron comprobaciones del callback con sesiones simuladas:

| Caso | Resultado |
|---|---|
| Sensor inexistente o inactivo | Cero filas añadidas y cero commits. |
| Magnitud no configurada | Cero filas añadidas y cero commits. |
| Unidad incorrecta, incluyendo diferencia de mayúsculas | Cero filas añadidas y cero commits. |
| Valor fuera de rango | Cero filas añadidas y cero commits. |
| Payload con dos magnitudes válidas | Dos filas añadidas en un único commit, ambas con el mismo timestamp UTC. |
| Timestamp sin zona, campo obligatorio ausente, tipo incorrecto o campo extra | Rechazado por el esquema Pydantic antes de consultar la base de datos. |

Las comprobaciones simuladas verifican la ruta del callback sin publicar datos
de prueba al tópico compartido del sensor.

## Claves foráneas y separación de responsabilidades

La consulta de `information_schema` confirmó las reglas existentes:

| Tabla hija | `ON UPDATE` | `ON DELETE` |
|---|---|---|
| `sensor_magnitudes` | CASCADE | RESTRICT |
| `mediciones` | CASCADE | RESTRICT |

La estructura separa los módulos `schemas/`, `models/`, `crud/`, `api/`,
`mqtt/` y `database/`. Los modelos son mapeos ORM; no se ejecuta creación de
tablas.
