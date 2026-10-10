import os
from sqlalchemy import inspect, create_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(URL)
inspector = inspect(engine)

print("Columnas reales en la tabla 'sensor_magnitudes':")
for columna in inspector.get_columns("sensor_magnitudes"):
    print(f"- {columna['name']}")