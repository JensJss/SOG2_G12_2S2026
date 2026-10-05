import os
import re
import sys
import unicodedata
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Reutiliza el agente y las herramientas definidas en servidor.py
from servidor import agent

MENSAJE_SOBRECARGA = (
    "Sobrecarga temporal en los servidores de Google. "
    "Vuelve a intentarlo en unos segundos."
)

PALABRAS_ERROR = [
    "429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE",
    "ResourceExhaustedError", "ServerError", "ClientError",
]

GRAFICOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "graficos"))

# ---------------------------------------------------------------------------
# Integración del módulo de Graficación (Integrante 4)
# Las gráficas se generan con el código de graficacion/graficas.py y
# graficacion/correlaciones.py, guardándose en GRAFICOS_DIR para servirlas.
# ---------------------------------------------------------------------------

_CANDIDATOS_GRAFICACION = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "graficacion"),
    "/graficacion",  # ruta montada dentro del contenedor Docker
]

GRAFICACION_DIR = next(
    (c for c in _CANDIDATOS_GRAFICACION if os.path.isdir(c)), None
)

if GRAFICACION_DIR is None:
    raise RuntimeError(
        "No se encontro el modulo de graficacion. Verifica el volumen del contenedor."
    )

if GRAFICACION_DIR not in sys.path:
    sys.path.insert(0, GRAFICACION_DIR)

import correlaciones  # noqa: E402  (módulo de graficacion/)
import graficas  # noqa: E402  (módulo de graficacion/)

# Redirige la salida de los generadores al directorio servido por la API
graficas.DIRECTORIO_SALIDA = GRAFICOS_DIR
correlaciones.DIRECTORIO_SALIDA = GRAFICOS_DIR


def _normalizar(texto: str) -> str:
    """Minúsculas sin acentos para comparar peticiones con palabras clave."""
    texto = texto.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


CATALOGO_GRAFICOS = [
    (
        ["matriz", "heatmap", "mapa de calor"],
        correlaciones.matriz_correlaciones,
        "Mapa de calor",
        "Matriz de Correlacion de Variables Numericas",
    ),
    (
        ["edad vs venta", "edad y venta", "correlacion edad", "pearson"],
        correlaciones.correlacion_edad_venta_total,
        "Dispersión con regresión",
        "Correlacion Edad vs Venta Total",
    ),
    (
        ["genero y metodo", "genero vs metodo", "correlacion genero"],
        correlaciones.correlacion_genero_metodo_pago,
        "Mapa de calor cruzado",
        "Correlacion Genero vs Metodo de Pago",
    ),
    (
        ["boletin y vale", "boletin vs vale", "correlacion boletin"],
        correlaciones.correlacion_boletin_vale,
        "Mapa de calor cruzado",
        "Correlacion Boletin vs Vale",
    ),
    (
        ["tendencia", "mensual", "por mes", "linea"],
        graficas.grafico_tendencia_mensual,
        "Líneas",
        "Tendencia de Ventas por Mes (2021)",
    ),
    (
        ["metodo de pago", "metodos de pago", "tarjeta", "efectivo"],
        graficas.grafico_ventas_metodo_pago,
        "Barras",
        "Ventas por Metodo de Pago",
    ),
    (
        ["navegador", "navegadores"],
        graficas.grafico_compras_navegador,
        "Barras horizontales",
        "Cantidad de Compras por Navegador",
    ),
    (
        ["histograma", "edades"],
        graficas.grafico_histograma_edades,
        "Histograma",
        "Distribucion de Edad de los Clientes",
    ),
    (
        ["genero", "pastel"],
        graficas.grafico_distribucion_genero,
        "Pastel",
        "Distribucion de Compras por Genero",
    ),
    (
        ["tiempo en el sitio", "tiempo sitio", "monto y tiempo", "dispersion monto"],
        graficas.grafico_dispersion_monto_tiempo,
        "Dispersión",
        "Monto de Compra vs Tiempo en el Sitio",
    ),
    (
        ["caja", "boxplot", "bigotes"],
        graficas.grafico_cajas_venta_genero,
        "Cajas",
        "Venta Total por Genero",
    ),
    (
        ["promocion", "boletin", "vale"],
        graficas.grafico_promociones,
        "Barras agrupadas",
        "Ventas por Uso de Boletin y Vale",
    ),
]


def _seleccionar_grafico(peticion: str):
    """Devuelve (funcion, tipo, titulo) según palabras clave, o None si no coincide."""
    normalizado = _normalizar(peticion)
    for claves, funcion, tipo, titulo in CATALOGO_GRAFICOS:
        if any(clave in normalizado for clave in claves):
            return funcion, tipo, titulo
    return None


def _texto_opciones() -> str:
    lineas = [
        "No se identificó una gráfica para tu petición. Opciones disponibles:",
        "",
    ]
    vistos: set[str] = set()
    for _claves, _funcion, tipo, titulo in CATALOGO_GRAFICOS:
        clave_catalogo = f"{titulo} ({tipo})"
        if clave_catalogo not in vistos:
            vistos.add(clave_catalogo)
            lineas.append(f"- {titulo} ({tipo})")
    lineas += [
        "",
        "Escribe por ejemplo: 'grafica de barras de metodos de pago' o 'tendencia de ventas por mes'.",
    ]
    return "\n".join(lineas)


app = FastAPI(title="Servidor IA - Analista de Datos", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
runner = Runner(agent=agent, session_service=session_service, app_name="servidor_api")


class PeticionConsulta(BaseModel):
    pregunta: str


class PeticionGrafico(BaseModel):
    peticion: str


class RespuestaConsulta(BaseModel):
    respuesta: str
    imagen: str | None = None


def _es_error_sobrecarga(texto: str) -> bool:
    return any(palabra in texto for palabra in PALABRAS_ERROR)


def _generar_desde_seleccion(seleccion) -> tuple[str, str, str]:
    """Ejecuta el generador del módulo de Graficación y devuelve (archivo, tipo, título)."""
    funcion, tipo, titulo = seleccion
    df = graficas.cargar_datos()
    # Mismo estilo que aplica el módulo de Graficación al generar sus gráficas
    graficas.sns.set_theme(style="whitegrid")
    ruta = funcion(df)
    return Path(ruta).name, tipo, titulo


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/consultar", response_model=RespuestaConsulta)
async def consultar(peticion: PeticionConsulta):
    """Envía una pregunta al agente y genera automáticamente la gráfica correspondiente.

    Devuelve la justificación del agente junto con la gráfica generada por el
    módulo de Graficación (si la pregunta coincide con alguna del catálogo).
    """
    pregunta = peticion.pregunta.strip()
    if not pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    # Generación automática de la gráfica con el módulo de Graficación
    imagen = None
    bloque_grafica = ""
    seleccion = _seleccionar_grafico(pregunta)
    if seleccion is not None:
        try:
            archivo, tipo, titulo = _generar_desde_seleccion(seleccion)
            imagen = archivo
            bloque_grafica = (
                "\n\n"
                "GRÁFICA GENERADA AUTOMÁTICAMENTE CON EL MÓDULO DE GRAFICACIÓN:\n"
                f"- Tipo: {tipo}\n"
                f"- Título: {titulo}\n"
                f"- Archivo: {archivo}"
            )
        except Exception as e:
            bloque_grafica = f"\n\nNota: no se pudo generar la gráfica automática ({e})."

    session_id = f"sesion_{uuid.uuid4().hex}"
    session_service.create_session_sync(
        app_name="servidor_api", user_id="usuario_web", session_id=session_id
    )

    partes_respuesta: list[str] = []
    try:
        events = runner.run_async(
            user_id="usuario_web",
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part.from_text(text=pregunta)]),
        )
        async for event in events:
            err_code = getattr(event, "error_code", None)
            err_msg = getattr(event, "error_message", None)
            if err_code or err_msg:
                detalle = str(err_msg or err_code)
                if _es_error_sobrecarga(detalle):
                    raise HTTPException(status_code=503, detail=MENSAJE_SOBRECARGA)
                partes_respuesta.append(f"Error en la consulta: {detalle}")
            elif event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        partes_respuesta.append(part.text)
    except HTTPException:
        raise
    except Exception as e:
        if _es_error_sobrecarga(str(e)):
            raise HTTPException(status_code=503, detail=MENSAJE_SOBRECARGA)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")

    respuesta = ("\n".join(partes_respuesta).strip() or MENSAJE_SOBRECARGA) + bloque_grafica

    # Si no hubo gráfica automática, detecta un PNG generado por el propio agente
    if imagen is None:
        coincidencia = re.search(r"([\w\-]+\.png)", respuesta, re.IGNORECASE)
        if coincidencia:
            nombre = coincidencia.group(1)
            if (Path(GRAFICOS_DIR) / nombre).exists():
                imagen = nombre

    return RespuestaConsulta(respuesta=respuesta, imagen=imagen)


@app.post("/api/graficar", response_model=RespuestaConsulta)
def graficar(peticion: PeticionGrafico):
    """Genera una gráfica con el módulo de Graficación según la petición del usuario.

    Selecciona el gráfico por palabras clave sobre `ventas.vw_ventas`, lo guarda
    como PNG y devuelve su descripción junto al nombre del archivo generado.
    """
    texto = peticion.peticion.strip()
    if not texto:
        raise HTTPException(status_code=400, detail="La petición no puede estar vacía.")

    seleccion = _seleccionar_grafico(texto)
    if seleccion is None:
        return RespuestaConsulta(respuesta=_texto_opciones(), imagen=None)

    try:
        archivo, tipo, titulo = _generar_desde_seleccion(seleccion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la gráfica: {e}")

    respuesta = (
        "GRÁFICA GENERADA CON EL MÓDULO DE GRAFICACIÓN:\n"
        f"- Tipo: {tipo}\n"
        f"- Título: {titulo}\n"
        f"- Archivo: {archivo}\n\n"
        "La visualización ya se muestra en la sección Visualización.\n"
        "Puedes solicitar otra gráfica (tendencia mensual, métodos de pago,\n"
        "navegadores, género, histograma de edades, dispersión, cajas,\n"
        "promociones o correlaciones)."
    )
    return RespuestaConsulta(respuesta=respuesta, imagen=archivo)


@app.get("/api/graficos")
async def listar_graficos():
    """Lista los gráficos PNG disponibles."""
    if not os.path.isdir(GRAFICOS_DIR):
        return {"graficos": []}
    archivos = [f for f in os.listdir(GRAFICOS_DIR) if f.lower().endswith(".png")]
    archivos.sort(key=lambda nombre: -os.path.getmtime(os.path.join(GRAFICOS_DIR, nombre)))
    return {"graficos": archivos}


@app.get("/api/graficos/{nombre}")
async def obtener_grafico(nombre: str):
    """Sirve un gráfico PNG generado por el backend."""
    if ".." in nombre or "/" in nombre or "\\" in nombre or not nombre.lower().endswith(".png"):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido.")
    ruta = Path(GRAFICOS_DIR) / nombre
    if not ruta.exists():
        raise HTTPException(status_code=404, detail="El gráfico solicitado no existe.")
    return FileResponse(ruta, media_type="image/png")
