"""Conexion compartida a la base de datos para el modulo de Graficacion (Integrante 4).

Lee las credenciales desde el archivo `.env` de la raiz de `Practica1` y
construye el engine de SQLAlchemy hacia el esquema `ventas` de PostgreSQL.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RUTA_ENV = os.path.join(DIRECTORIO_SCRIPT, "..", ".env")


def obtener_engine():
    """Construye y retorna la conexion SQLAlchemy hacia PostgreSQL."""
    if os.path.exists(RUTA_ENV):
        load_dotenv(RUTA_ENV)
    else:
        load_dotenv()

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "ventas_online")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    sslmode = os.getenv("DB_SSLMODE", "prefer")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}?sslmode={sslmode}"
    return create_engine(url, pool_pre_ping=True)
