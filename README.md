# API IoT — Taller 2

API desarrollada con FastAPI para recibir mediciones IoT por MQTT, validarlas
con Pydantic y SQLAlchemy, almacenarlas en PostgreSQL y consultarlas mediante
endpoints HTTP.

## 1. Información general

| Dato | Valor |
|---|---|
| Asignatura | Aplicaciones y Servicios Web |
| Fecha de revisión y pruebas | 10 de octubre de 2026 |
| Sensor asignado | `GAS-001` |
| Tópico MQTT | `iot/sensors/GAS-001/data` |
| Integrantes | Simon Herrera Acosta y Juan David Arias Ospina |

## 2. Descripción y arquitectura

El consumidor MQTT recibe el mensaje JSON publicado por el sensor. Pydantic
valida su estructura, los campos, los tipos y el timestamp con zona horaria.
Luego la aplicación consulta en PostgreSQL el sensor y sus magnitudes, valida
su estado, unidad y límites, y almacena una fila por cada magnitud válida.
Todas las filas producidas por un mismo payload usan el mismo `timestamp_utc`.

Un payload real de referencia, reconstruido a partir de las mediciones
almacenadas que comparten timestamp, fue:

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

La aplicación no conserva el texto JSON original del broker; este ejemplo se
reconstruyó con los registros de `mediciones` para documentar datos recibidos y
persistidos.

## 3. Configuración del entorno

Se utilizó Python 3.12.10 en Windows. Desde la raíz del proyecto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crear un archivo `.env` local con los siguientes nombres de variables. Los
valores reales no deben subirse al repositorio:

```dotenv
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=
MQTT_BROKER=
MQTT_PORT=1883
MQTT_TOPIC=iot/sensors/GAS-001/data
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_KEEPALIVE=60
```

Para iniciar la API y el consumidor MQTT:

```powershell
python -m uvicorn app.main:app --reload
```

La aplicación inicia MQTT durante su `lifespan` y detiene el consumidor al
cerrarse. La documentación interactiva de la API está disponible en
`/docs`.

## 4. Base de datos

La aplicación utiliza las tablas PostgreSQL existentes `sensores`,
`sensor_magnitudes` y `mediciones`. El catálogo de sensores y magnitudes solo
se consulta; la aplicación no crea ni modifica esas tablas maestras.

Las relaciones son `sensores` 1:N `sensor_magnitudes` y
`sensor_magnitudes` 1:N `mediciones`. Las claves foráneas usan `ON UPDATE
CASCADE ON DELETE RESTRICT`, verificado en la base. Los modelos ORM mapean el
esquema existente; no se llama a `Base.metadata.create_all()`.

El detalle de columnas, tipos e índices está en [data-model.md](./data-model.md).
La conexión usa `pool_pre_ping=True`.

## 5. Organización del código

| Directorio/archivo | Responsabilidad |
|---|---|
| `app/schemas/` | Esquemas Pydantic para respuestas y payloads MQTT. |
| `app/models/` | Mapeos ORM de las tablas PostgreSQL existentes. |
| `app/crud/` | Consultas y persistencia de las entidades. |
| `app/api/` | Rutas HTTP, parámetros, respuestas y errores. |
| `app/mqtt/cliente.py` | Suscripción MQTT, validación de negocio y almacenamiento atómico del payload. |
| `app/database/connection.py` | Motor y sesiones SQLAlchemy. |
| `scripts/` | Utilidades auxiliares, como inspección de columnas. |


## 6. Endpoints implementados

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/sensores` | Lista sensores. |
| GET | `/sensores/{sensor_id}` | Consulta un sensor por ID. |
| GET | `/sensores/por-codigo/{codigo}` | Consulta un sensor por código. |
| GET | `/sensores/{sensor_id}/magnitudes` | Lista las magnitudes configuradas para un sensor. |
| GET | `/sensor-magnitudes/{magnitud_id}` | Consulta una magnitud por ID. |
| GET | `/mediciones/{medicion_id}` | Consulta una medición por ID. |
| GET | `/sensores/{sensor_id}/mediciones` | Consulta histórico con filtros combinables `magnitud`, `desde`, `hasta` y `limit`. |
| GET | `/sensores/{sensor_id}/ultima-medicion` | Consulta la medición más reciente del sensor. |
| GET | `/sensores/{sensor_id}/mediciones/ultima` | Alias de compatibilidad para la consulta de última medición. |

Los límites `desde` y `hasta` requieren zona horaria. Si `desde` es posterior a
`hasta`, el endpoint devuelve `400`; un `limit` menor que 1 o un parámetro con
formato/tipo inválido produce `422`. Las respuestas de mediciones incluyen
`timestamp_utc` normalizado a UTC y `timestamp_local` en hora de Colombia
(UTC−05:00).

## 7. Pruebas y evidencias

El resumen de las pruebas y observaciones, incluyendo las respuestas HTTP, la
captura MQTT superior a 20 minutos, los datos persistidos y los payloads
rechazados, está en [evidencias/validacion.md](./evidencias/validacion.md).

## 8. Control de versiones y aportes

- Repositorio del equipo: [apps_services_2, rama `taller-2`](https://github.com/Juanda555-bit/apps_services_2/tree/taller-2).

| Integrante | Usuario GitHub | Aportes y commits reportados |
|---|---|---|
| Simon Herrera Acosta | `Simonh003` | Configuración inicial de la arquitectura, conexión a PostgreSQL y modelo ORM `Sensor`. |
| Juan David Arias Ospina | `Juanda555-bit` | Configuración de base de datos, modelos ORM, esquemas Pydantic, CRUD y cliente MQTT; reconstrucción de enrutadores, conexión a base de datos y corrección de modelos. |

El historial del repositorio enlazado contiene los commits identificables de
ambos integrantes.

## 9. Conclusiones

El desarrollo permitió integrar el consumidor MQTT al ciclo de vida de
FastAPI, ejecutándolo en segundo plano sin bloquear las solicitudes HTTP.
También permitió aplicar validación estricta con Pydantic antes de acceder a
la base de datos y consolidar una arquitectura modular que separa modelos ORM,
esquemas, operaciones CRUD, rutas API y cliente MQTT.

Durante la integración se abordaron dificultades de resolución DNS del broker
`emqx.coriotlab.co`, conexiones PostgreSQL que podían cerrarse tras periodos
de inactividad y rutas absolutas de Uvicorn que dejaron de ser válidas al
reubicar el proyecto. El diagnóstico de red con `nslookup` permitió configurar
la dirección IP del broker en el entorno local; `pool_pre_ping=True` habilitó
la comprobación de conexiones inactivas antes de utilizarlas; y la
reconstrucción del entorno virtual con las dependencias de
`requirements.txt` restableció los ejecutables de Python.

Las verificaciones confirmaron el funcionamiento de los endpoints requeridos
y de los códigos HTTP `200`, `400`, `404` y `422`. En una recepción de más de
20 minutos para `GAS-001`, el número de mediciones asociadas al sensor aumentó
en 470 registros. Se observaron en los logs mensajes MQTT inválidos
descartados, y las pruebas controladas del callback confirmaron que un payload
con una magnitud inválida no produce commits parciales, mientras que las
magnitudes válidas se almacenan con un mismo timestamp UTC. La base de datos
confirmó las reglas de claves foráneas `ON UPDATE CASCADE ON DELETE RESTRICT`.
Las respuestas de mediciones incluyen el timestamp UTC y su representación
local de Colombia.
