#print("Hola, Aplicaciones y Servicios Web")
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RUTA_CSV = BASE_DIR / "datos" / "estudiantes.csv"

def leer_estudiantes(ruta: Path) -> list[dict]:
    """Lee el CSV y devuelve una lista de diccionarios (uno por fila)."""
    with open(ruta, encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        return list(lector)

estudiantes = leer_estudiantes(RUTA_CSV)

def transformar_estudiante(estudiante: dict) -> dict:
    """Convierte un registro crudo del CSV al formato del panel académico."""
    return {
        "id": estudiante["codigo"],
        "nombre_completo": f'{estudiante["nombre"]} {estudiante["apellido"]}',
        "semestre": int(estudiante["semestre"]),
        "promedio": float(estudiante["promedio"]),
        "estado": "Activo" if estudiante["activo"] == "true" else "Inactivo",
    }

def serializar_estudiantes(ruta: Path, estudiantes: list[dict]) -> None:
    """Serializa una lista de diccionarios Python a un archivo JSON UTF-8."""
    ruta.parent.mkdir(exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(estudiantes, archivo, indent=2, ensure_ascii=False)

def deserializar_estudiantes(ruta: Path) -> list[dict]:
    """Deserializa un archivo JSON a una lista de diccionarios Python."""
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)

estudiantes_transformados = [transformar_estudiante(e) for e in estudiantes]

print(f"Total transformados: {len(estudiantes_transformados)}")
print(estudiantes_transformados[0])
print(estudiantes_transformados[-1])
RUTA_JSON = BASE_DIR / "salida" / "estudiantes_resumen.json"

serializar_estudiantes(RUTA_JSON, estudiantes_transformados)
print(f"Archivo JSON generado: {RUTA_JSON}")

estudiantes_recuperados = deserializar_estudiantes(RUTA_JSON)

print("\nDatos recuperados desde el JSON:")
print(estudiantes_recuperados[0])
print(f"Total recuperado: {len(estudiantes_recuperados)}")