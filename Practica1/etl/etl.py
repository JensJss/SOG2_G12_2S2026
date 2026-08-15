"""
SOG2 - Practica 1 - Segundo Semestre 2026
ETL: Extraccion, Limpieza y Carga (Ventas Online 2021 -> PostgreSQL / RDS)

Responsable: Integrante 1 - Base de Datos y ETL

Uso:
    python etl.py
    python etl.py --dry-run    (no escribe en BD, solo valida)
    python etl.py --truncate   (vacia clientes/compras antes de cargar)

Por defecto el script busca "Venta_online_c.csv" en el mismo directorio
donde se encuentra este archivo etl.py (no es necesario pasar la ruta).
Si se desea usar otro archivo/ubicacion, se puede indicar con --csv.

Requiere un archivo .env (ver .env.example) con las credenciales de RDS.
"""

import argparse
import logging
import os
import sys
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# ---------------------------------------------------------------------------
# Ruta por defecto del CSV: mismo directorio donde vive este archivo etl.py
# ---------------------------------------------------------------------------
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CSV_POR_DEFECTO = os.path.join(DIRECTORIO_SCRIPT, "Venta_online_c.csv")

# ---------------------------------------------------------------------------
# Configuracion de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("etl_ventas_online")

# ---------------------------------------------------------------------------
# Definicion de columnas esperadas segun el enunciado de la practica
# ---------------------------------------------------------------------------
COLUMNAS_ESPERADAS = [
    "Id_cliente", "Edad", "Genero", "Venta_total", "N_Compras",
    "FechaCompra", "MontoCompra", "MetodoPago", "Tiempo",
    "Navegador", "Boletin", "Vale",
]

GENERO_VALIDOS = {0, 1}
METODO_PAGO_VALIDOS = {0, 1, 2}
NAVEGADOR_VALIDOS = {0, 1, 2, 3, 4}
BOOL_VALIDOS = {0, 1}


# ---------------------------------------------------------------------------
# 1. EXTRACCION
# ---------------------------------------------------------------------------
def extraer(csv_path: str) -> pd.DataFrame:
    """Lee el CSV de origen. El archivo entregado usa ';' como separador."""
    log.info("Extrayendo datos desde: %s", csv_path)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontro el archivo CSV: {csv_path}")

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")

    faltantes = set(COLUMNAS_ESPERADAS) - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas esperadas en el CSV: {faltantes}")

    log.info("Filas leidas: %d | Columnas: %d", len(df), len(df.columns))
    return df


# ---------------------------------------------------------------------------
# 2. LIMPIEZA / VALIDACION
# ---------------------------------------------------------------------------
def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica las reglas de limpieza descritas en el informe:
      - Elimina duplicados exactos y duplicados por Id_cliente (se conserva
        el primer registro y se deja log de cuantos se descartaron).
      - Elimina filas con valores nulos en columnas criticas.
      - Convierte tipos de datos (fechas, decimales, enteros, booleanos).
      - Valida que los campos categoricos esten dentro del dominio permitido
        (Genero, MetodoPago, Navegador, Boletin, Vale).
      - Descarta / reporta filas con edades o montos fuera de rango logico.
    """
    df = df.copy()
    filas_iniciales = len(df)

    # --- Duplicados exactos ---
    dup_exactos = df.duplicated().sum()
    if dup_exactos:
        log.warning("Duplicados exactos encontrados y eliminados: %d", dup_exactos)
    df = df.drop_duplicates()

    # --- Duplicados por llave de negocio (Id_cliente) ---
    dup_llave = df.duplicated(subset=["Id_cliente"]).sum()
    if dup_llave:
        log.warning(
            "Id_cliente duplicados encontrados: %d. Se conserva la primera ocurrencia.",
            dup_llave,
        )
    df = df.drop_duplicates(subset=["Id_cliente"], keep="first")

    # --- Nulos en columnas criticas ---
    antes = len(df)
    df = df.dropna(subset=COLUMNAS_ESPERADAS)
    nulos_eliminados = antes - len(df)
    if nulos_eliminados:
        log.warning("Filas con valores nulos eliminadas: %d", nulos_eliminados)

    # --- Tipos de datos ---
    df["Id_cliente"] = df["Id_cliente"].astype(int)
    df["Edad"] = df["Edad"].astype(int)
    df["Genero"] = df["Genero"].astype(int)
    df["Venta_total"] = df["Venta_total"].astype(float)
    df["N_Compras"] = df["N_Compras"].astype(int)
    df["MontoCompra"] = df["MontoCompra"].astype(float)
    df["MetodoPago"] = df["MetodoPago"].astype(int)
    df["Tiempo"] = df["Tiempo"].astype(int)
    df["Navegador"] = df["Navegador"].astype(int)
    df["Boletin"] = df["Boletin"].astype(int)
    df["Vale"] = df["Vale"].astype(int)

    # FechaCompra viene como DD.MM.YY (ej. 02.02.21 -> 2021-02-02)
    df["FechaCompra"] = pd.to_datetime(
        df["FechaCompra"], format="%d.%m.%y", errors="coerce"
    )
    fechas_invalidas = df["FechaCompra"].isna().sum()
    if fechas_invalidas:
        log.warning("Fechas invalidas eliminadas: %d", fechas_invalidas)
    df = df.dropna(subset=["FechaCompra"])

    # --- Validacion de dominios categoricos ---
    mascara_valida = (
        df["Genero"].isin(GENERO_VALIDOS)
        & df["MetodoPago"].isin(METODO_PAGO_VALIDOS)
        & df["Navegador"].isin(NAVEGADOR_VALIDOS)
        & df["Boletin"].isin(BOOL_VALIDOS)
        & df["Vale"].isin(BOOL_VALIDOS)
    )
    invalidos = (~mascara_valida).sum()
    if invalidos:
        log.warning("Filas con codigos categoricos fuera de dominio eliminadas: %d", invalidos)
    df = df[mascara_valida]

    # --- Validacion de rangos logicos ---
    mascara_rangos = (
        df["Edad"].between(0, 120)
        & (df["Venta_total"] >= 0)
        & (df["MontoCompra"] >= 0)
        & (df["N_Compras"] >= 0)
        & (df["Tiempo"] >= 0)
    )
    fuera_de_rango = (~mascara_rangos).sum()
    if fuera_de_rango:
        log.warning("Filas con valores fuera de rango logico eliminadas: %d", fuera_de_rango)
    df = df[mascara_rangos]

    # --- Booleanos ---
    df["Boletin"] = df["Boletin"].astype(bool)
    df["Vale"] = df["Vale"].astype(bool)

    log.info(
        "Limpieza finalizada. Filas iniciales: %d -> Filas finales: %d (descartadas: %d)",
        filas_iniciales, len(df), filas_iniciales - len(df),
    )
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. TRANSFORMACION A MODELO RELACIONAL (clientes / compras)
# ---------------------------------------------------------------------------
def transformar(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa el dataframe plano del CSV en las dos tablas del modelo."""
    clientes = df[["Id_cliente", "Edad", "Genero", "Venta_total", "N_Compras"]].rename(
        columns={
            "Id_cliente": "id_cliente",
            "Edad": "edad",
            "Genero": "id_genero",
            "Venta_total": "venta_total",
            "N_Compras": "n_compras",
        }
    )

    compras = df[[
        "Id_cliente", "FechaCompra", "MontoCompra", "MetodoPago",
        "Tiempo", "Navegador", "Boletin", "Vale",
    ]].rename(
        columns={
            "Id_cliente": "id_cliente",
            "FechaCompra": "fecha_compra",
            "MontoCompra": "monto_compra",
            "MetodoPago": "id_metodo_pago",
            "Tiempo": "tiempo_sitio",
            "Navegador": "id_navegador",
            "Boletin": "boletin",
            "Vale": "vale",
        }
    )
    compras["origen_carga"] = "csv_2021"

    return clientes, compras


# ---------------------------------------------------------------------------
# 4. CARGA
# ---------------------------------------------------------------------------
def construir_engine() -> Engine:
    """Construye el engine de SQLAlchemy a partir de variables de entorno (.env)."""
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    sslmode = os.getenv("DB_SSLMODE", "prefer")  # 'prefer': usa SSL si esta disponible
                                                   # (RDS) y funciona igual sin cambios
                                                   # contra un Postgres local sin SSL
                                                   # (ej. docker postgres:15-alpine).

    faltantes = [k for k, v in {
        "DB_HOST": host, "DB_NAME": name, "DB_USER": user, "DB_PASSWORD": password,
    }.items() if not v]
    if faltantes:
        raise EnvironmentError(
            f"Faltan variables de entorno requeridas: {faltantes}. "
            f"Revisa tu archivo .env (ver .env.example)."
        )

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}?sslmode={sslmode}"
    return create_engine(url, pool_pre_ping=True)


def truncar_tablas(engine: Engine) -> None:
    log.warning("Vaciando tablas ventas.compras y ventas.clientes (TRUNCATE CASCADE)...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE ventas.compras RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE ventas.clientes CASCADE;"))


def cargar(engine: Engine, clientes: pd.DataFrame, compras: pd.DataFrame) -> None:
    log.info("Cargando %d clientes...", len(clientes))
    clientes.to_sql(
        "clientes", con=engine, schema="ventas",
        if_exists="append", index=False, method="multi", chunksize=500,
    )

    log.info("Cargando %d compras...", len(compras))
    compras.to_sql(
        "compras", con=engine, schema="ventas",
        if_exists="append", index=False, method="multi", chunksize=500,
    )
    log.info("Carga finalizada correctamente.")


def verificar_carga(engine: Engine) -> None:
    with engine.connect() as conn:
        total_clientes = conn.execute(text("SELECT COUNT(*) FROM ventas.clientes")).scalar()
        total_compras = conn.execute(text("SELECT COUNT(*) FROM ventas.compras")).scalar()
    log.info("Verificacion post-carga -> clientes: %d | compras: %d", total_clientes, total_compras)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ETL Ventas Online 2021 -> PostgreSQL (RDS)")
    parser.add_argument(
        "--csv",
        default=CSV_POR_DEFECTO,
        help=(
            "Ruta al archivo .csv de ventas. Por defecto: "
            "'Venta_online_c.csv' en el mismo directorio que etl.py."
        ),
    )
    parser.add_argument("--truncate", action="store_true", help="Vaciar tablas antes de cargar")
    parser.add_argument("--dry-run", action="store_true", help="Solo extraer/limpiar, no escribe en BD")
    parser.add_argument("--env-file", default=".env", help="Ruta al archivo .env (default: .env)")
    args = parser.parse_args()

    load_dotenv(dotenv_path=args.env_file)

    inicio = datetime.now()
    log.info("===== INICIO ETL Ventas Online =====")
    log.info("Archivo CSV a procesar: %s", args.csv)

    df_crudo = extraer(args.csv)
    df_limpio = limpiar(df_crudo)
    clientes, compras = transformar(df_limpio)

    if args.dry_run:
        log.info("Modo --dry-run activo: no se escribira en la base de datos.")
        log.info("Ejemplo clientes:\n%s", clientes.head())
        log.info("Ejemplo compras:\n%s", compras.head())
    else:
        engine = construir_engine()
        if args.truncate:
            truncar_tablas(engine)
        cargar(engine, clientes, compras)
        verificar_carga(engine)

    duracion = (datetime.now() - inicio).total_seconds()
    log.info("===== FIN ETL Ventas Online (%.2f s) =====", duracion)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.exception("El proceso ETL fallo: %s", exc)
        sys.exit(1)
