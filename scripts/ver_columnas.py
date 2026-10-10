from sqlalchemy import inspect

from app.database.connection import engine


def main() -> None:
    inspector = inspect(engine)

    print("Columnas reales en la tabla 'sensor_magnitudes':")
    for column in inspector.get_columns("sensor_magnitudes"):
        print(f"- {column['name']}")


if __name__ == "__main__":
    main()