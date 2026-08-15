import csv
import json
import logging
import os
import sys
import time
import threading
import warnings
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Librerías de gráficos y procesamiento de datos 
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


# Silenciar advertencias secundarias y trazas de librerías en la consola
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
logging.disable(logging.CRITICAL)
threading.excepthook = lambda args: None

# Cargar variables de entorno (.env) desde el directorio actual o raíz del proyecto
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_env_raiz = os.path.join(directorio_actual, "..", ".env")

if os.path.exists(ruta_env_raiz):
    load_dotenv(ruta_env_raiz)
else:
    load_dotenv()


if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")


def obtener_engine_db():
    """Construye y retorna la conexión SQLAlchemy hacia la base de datos PostgreSQL."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "ventas_online")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    sslmode = os.getenv("DB_SSLMODE", "prefer")
    
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}?sslmode={sslmode}"
    return create_engine(url, pool_pre_ping=True)


def ejecutar_consulta_sql(query: str) -> str:
    """Ejecuta una consulta SQL de lectura en la base de datos PostgreSQL.
    
    Permite consultar directamente la vista `ventas.vw_ventas` u otras tablas del esquema `ventas`.
    
    Args:
        query: Consulta SQL SELECT a ejecutar.
        
    Returns:
        JSON con los resultados de la consulta o un mensaje con el error producido si la sintaxis falla.
    """
    query_clean = query.strip()
    
    # Validación básica de seguridad: solo permitir lectura
    if not (query_clean.upper().startswith("SELECT") or query_clean.upper().startswith("WITH")):
        return "Error: Solo se permiten consultas de lectura (SELECT o WITH)."
        
    try:
        engine = obtener_engine_db()
        with engine.connect() as conn:
            result = conn.execute(text(query_clean))
            keys = result.keys()
            filas = [dict(zip(keys, row)) for row in result.fetchall()]
            
            resumen = {
                "total_filas_retornadas": len(filas),
                "muestra_datos": filas[:100]  
            }
            return json.dumps(resumen, default=str, ensure_ascii=False)
    except Exception as e:
        return f"Error de sintaxis o ejecución SQL: {str(e)}"





def generar_grafico(tipo_grafico: str, consulta_sql: str, columna_x: str, columna_y: str = "", titulo: str = "Grafico Estadistico", nombre_archivo: str = "grafico.png") -> str:
    """Genera y guarda una imagen PNG de un gráfico estadístico a partir de una consulta SQL en PostgreSQL.
    
    Args:
        tipo_grafico: Tipo de gráfico a generar ('barras', 'lineas', 'dispersión', 'pastel', 'histograma', 'cajas').
        consulta_sql: Consulta SQL SELECT que obtiene los datos necesarios.
        columna_x: Nombre de la columna para el eje X (o etiquetas en gráfico pastel).
        columna_y: Nombre de la columna para el eje Y (opcional para histogramas/pastel).
        titulo: Título descriptivo para la gráfica.
        nombre_archivo: Nombre del archivo de salida PNG (ejemplo: 'ventas_por_mes.png').
        
    Returns:
        Mensaje confirmando la creación exitosa del archivo PNG y la ruta exacta donde se guardó.
    """
    try:
        engine = obtener_engine_db()
        with engine.connect() as conn:
            df = pd.read_sql_query(text(consulta_sql), conn)
            
        if df.empty:
            return f"Error: La consulta SQL no devolvió datos para generar el gráfico."
            
        # Crear directorio para guardar gráficos si no existe
        directorio_graficos = os.path.abspath(os.path.join(directorio_actual, "..", "graficos"))
        os.makedirs(directorio_graficos, exist_ok=True)
        if not nombre_archivo.endswith(".png"):
            nombre_archivo += ".png"
        ruta_salida = os.path.join(directorio_graficos, nombre_archivo)
        
        # Estilo visual limpio y moderno
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        
        tipo = tipo_grafico.lower().strip()
        
        if any(k in tipo for k in ['barra', 'bar']):
            sns.barplot(data=df, x=columna_x, y=columna_y if columna_y in df.columns else None, ax=ax, palette='crest')
            plt.xticks(rotation=45, ha='right')
        elif any(k in tipo for k in ['linea', 'line']):
            sns.lineplot(data=df, x=columna_x, y=columna_y, ax=ax, marker='o', color='#2b5c8f', linewidth=2.5)
            plt.xticks(rotation=45, ha='right')
        elif any(k in tipo for k in ['dispersion', 'scatter']):
            sns.scatterplot(data=df, x=columna_x, y=columna_y, ax=ax, color='#e74c3c', s=70, alpha=0.7)
        elif any(k in tipo for k in ['pastel', 'pie']):
            col_val = columna_y if columna_y in df.columns else df.columns[1]
            ax.pie(df[col_val], labels=df[columna_x], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
        elif any(k in tipo for k in ['hist', 'histograma']):
            sns.histplot(data=df, x=columna_x, kde=True, ax=ax, color='#3498db')
        elif any(k in tipo for k in ['caja', 'box']):
            sns.boxplot(data=df, x=columna_x, y=columna_y if columna_y in df.columns else None, ax=ax, palette='Set2')
        else:
            sns.barplot(data=df, x=columna_x, y=columna_y if columna_y in df.columns else None, ax=ax, palette='viridis')
            plt.xticks(rotation=45, ha='right')
            
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
        if columna_x and not any(k in tipo for k in ['pastel', 'pie']):
            ax.set_xlabel(columna_x.replace('_', ' ').title(), fontsize=11, fontweight='bold')
        if columna_y and not any(k in tipo for k in ['pastel', 'pie']):
            ax.set_ylabel(columna_y.replace('_', ' ').title(), fontsize=11, fontweight='bold')
            
        plt.tight_layout()
        plt.savefig(ruta_salida, dpi=300)
        plt.close(fig)
        
        return f"Gráfico '{titulo}' generado y guardado exitosamente en: {ruta_salida}"
    except Exception as e:
        return f"Error al generar el gráfico: {str(e)}"


# Instrucciones detalladas enviadas al Agente
INSTRUCCIONES_AGENTE = """Eres un Analista de Datos Junior encargado de responder consultas sobre las ventas online del año 2021.

Interactúas con los usuarios a través de una consola y tienes acceso a una base de datos PostgreSQL. Para responder, SIEMPRE debes generar y ejecutar consultas SQL utilizando las herramientas proporcionadas.

INFORMACIÓN CLAVE DE LA BASE DE DATOS:
Tienes a tu disposición una vista consolidada llamada `ventas.vw_ventas` que ya tiene todos los JOINs resueltos.
Las columnas principales de esta vista incluyen datos del cliente (id_cliente, edad, genero, venta_total, n_compras) y datos de la transacción (id_compra, fecha_compra, mes_compra, anio_compra, monto_compra, metodo_pago, tiempo_sitio, navegador, boletin, vale).
Los textos de los catálogos ya están resueltos en la vista, por lo que no necesitas cruzar tablas.

REGLAS ESTRICTAS:
1. CERO SUPOSICIONES: Nunca inventes ni estimes datos. Utiliza siempre la herramienta de ejecución SQL.
2. USA LA VISTA: Prioriza hacer tus consultas `SELECT` siempre sobre el esquema y vista `ventas.vw_ventas`.
3. ANÁLISIS DE INGENIERÍA: Cuando calcules tendencias, segmentes clientes o busques correlaciones, analiza los resultados del SQL y entrega una explicación clara, estructurada y lista para un informe gerencial.
4. AUTOCORRECCIÓN: Si tu consulta SQL falla por un error de sintaxis, analiza el error, corrige el código y vuelve a intentarlo antes de responder al usuario.
5. GENERACIÓN DE GRÁFICOS / VISUALIZACIONES: Cuando el usuario te pida un gráfico, gráfica, diagrama o representación visual (de barras, líneas, dispersión, pastel, histograma o cajas), utiliza OBLIGATORIAMENTE la herramienta `generar_grafico` especificando la consulta SQL adecuada, el tipo de gráfico, la columna X, la columna Y, un título claro y guardándolo como archivo PNG. Informa al usuario la ruta del archivo generado.
"""

# Configurar el Agente
agent = Agent(
    name="AnalistaDatosJunior",
    model="gemini-3.6-flash",
    instruction=INSTRUCCIONES_AGENTE,
    tools=[ejecutar_consulta_sql, generar_grafico],
)

def consultar_agente(runner: Runner, pregunta: str, session_id: str = "sesion_1"):
    """Envía una pregunta al agente con manejo limpio de sobrecarga de servidor."""
    try:
        events = runner.run(
            user_id="usuario_consola",
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part.from_text(text=pregunta)])
        )
        
        print("\n" + "="*65)
        print(" RESPUESTA DE LA IA:")
        print("="*65)
        
        hubo_respuesta = False
        for event in events:
            err_code = getattr(event, "error_code", None)
            err_msg = getattr(event, "error_message", None)
            
            if err_code or err_msg:
                hubo_respuesta = True
                if any(k in str(err_msg) or k in str(err_code) for k in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "ResourceExhaustedError", "ServerError", "ClientError"]):
                    print(" Sobrecarga temporal en los servidores de Google. Simplemente vuelve a escribir tu pregunta unos segundos después y responderá normalmente.")
                else:
                    print(f" Error en la consulta: {err_msg or err_code}")
            elif event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        hubo_respuesta = True
                        print(part.text)
        
        if not hubo_respuesta:
            print(" Sobrecarga temporal en los servidores de Google. Simplemente vuelve a escribir tu pregunta unos segundos después y responderá normalmente.")
            
        print("="*65 + "\n")
    except Exception as e:
        if any(k in str(e) for k in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "ServerError", "ClientError"]):
            print("\n" + "="*65)
            print(" Sobrecarga temporal en los servidores de Google. Simplemente vuelve a escribir tu pregunta unos segundos después y responderá normalmente.")
            print("="*65 + "\n")
        else:
            print(f"\n Ocurrió un error inesperado: {e}\n")



if __name__ == "__main__":
    print("\n" + "="*65)
    print(" SERVIDOR MCP / AGENTE ANALISTA DE DATOS (POSTGRESQL)")
    print("="*65)
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name="servidor_mcp"
    )
    session_service.create_session_sync(app_name="servidor_mcp", user_id="usuario_consola", session_id="sesion_1")
    
    # 1. Prueba inicial automática
    pregunta_inicial = "¿Cuáles son las columnas disponibles en ventas.vw_ventas y cuántos registros hay en total?"
    print(f" CONSULTA DE INICIALIZACIÓN: {pregunta_inicial}")
    consultar_agente(runner, pregunta_inicial)
    
    # 2. Modo de Consola Interactivo
    print("\nMODO DE CONSULTAS INTERACTIVO")
    print("Escribe cualquier pregunta sobre los datos de ventas 2021 (o 'salir' para terminar):")
    print("-" * 65)
    
    while True:
        try:
            pregunta_usuario = input("\n--> Pregunta: ").strip()
            if not pregunta_usuario:
                continue
            if pregunta_usuario.lower() in ["salir", "exit", "quit", "q"]:
                print("\n Servidor MCP finalizado. ¡Hasta luego!\n")
                break
                
            consultar_agente(runner, pregunta_usuario)
        except (KeyboardInterrupt, EOFError):
            print("\nServidor MCP finalizado.")
            break