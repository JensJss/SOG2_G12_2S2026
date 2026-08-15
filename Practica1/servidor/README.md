#  Servidor MCP - Agente de IA Conversacional (Ventas 2021)

Este directorio contiene la implementación del **Servidor MCP y Agente de Inteligencia Artificial Conversacional**, desarrollado para analizar los datos de ventas online del año 2021 almacenados en la base de datos PostgreSQL.

El agente utiliza **Google ADK (Agent Development Kit)** junto con el modelo **Google Gemini 3.6 Flash** y cuenta con capacidades para ejecutar consultas SQL dinámicas y generar gráficos estadísticos automáticamente.

---

##  Arquitectura e Integración Técnica

###  Componentes Principales

![imagen_arquitectura](/Practica1/servidor/Arquitectura.png)

##  Herramientas Registradas (Tools)

### 1. `ejecutar_consulta_sql`
- **Propósito:** Genera y ejecuta consultas de lectura (`SELECT`) dinámicas directamente contra la vista consolidada `ventas.vw_ventas`.
- **Manejo de Tokens:** Retorna un objeto JSON con métricas consolidadas y muestra controlada de filas para evitar errores de cuota por volumen de texto.
- **Autocorrección:** Si una consulta falla por sintaxis, el error es devuelto al agente para que corrija la instrucción SQL automáticamente antes de responder al usuario.

### 2. `generar_grafico`
- **Propósito:** Crea y guarda gráficos estadísticos en alta resolución (300 DPI) en formato `.png` dentro del directorio `graficos/`.
- **Tipos de Gráficos Soportados:**
  -  **Barras (`barras`):** Para comparaciones categóricas (métodos de pago, navegadores).
  -  **Líneas (`lineas`):** Para análisis de tendencias temporales (ventas por mes).
  -  **Dispersión (`dispersión`):** Para evaluar correlaciones (edad vs. venta total).
  -  **Pastel (`pastel`):** Para proporciones de participación.
  -  **Histograma (`histograma`):** Para distribuciones de frecuencia.
  -  **Cajas (`cajas`):** Para análisis de dispersión y cuartiles.

---

##  Resiliencia y Control de Errores

- **Supresión de Trazas Secundarias:** Se silenciaron las trazas de depuración de librerías mediante `logging.disable(logging.CRITICAL)` y la redirección de excepciones de hilos secundarios (`threading.excepthook`).
- **Manejo de Sobrecarga de API:** Si los servidores de Google experimentan alta demanda (`503 UNAVAILABLE`) o se alcanza el límite de peticiones (`429 RESOURCE_EXHAUSTED`), el sistema captura el evento y muestra una notificación amigable en consola en lugar de detener la ejecución.

---

##  Requisitos del Entorno

Asegúrate de contar con el entorno virtual activado e instalar las dependencias especificadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Contenido de `requirements.txt`:
```text
google-adk
python-dotenv
sqlalchemy
psycopg2-binary
matplotlib
seaborn
pandas
```

### Configuración del `.env`:
El servidor requiere que las siguientes variables estén definidas en el archivo `.env` (en la raíz del proyecto o en este directorio):

```env
GOOGLE_API_KEY="tu_api_key_de_gemini"

DB_HOST="compras-postgres.ckxkewa2qxns.us-east-1.rds.amazonaws.com"
DB_PORT=5432
DB_NAME="ventas_online"
DB_USER="postgres"
DB_PASSWORD="tu_password"
```

---

##  Instrucciones de Ejecución

### Opción 1: Ejecución Local en Consola
Navega a la carpeta del servidor y ejecuta `servidor.py`:

```bash
cd servidor
python servidor.py
```

Al iniciar, el sistema realizará una consulta automática de verificación y habilitará el **Modo de Consultas Interactivo**, donde podrás escribir cualquier pregunta en lenguaje natural.

### Opción 2: Despliegue con Docker Compose
Si prefieres ejecutar todo el stack (PostgreSQL + Servidor IA) en contenedores:

```bash
# Desde la raíz de Practica1
docker compose up --build
```

---

##  Ejemplos de Consultas Disponibles

Puedes hacerle al agente preguntas como:

- **Análisis de Tendencias:**
  - *¿Cuáles fueron los meses con mayores y menores ventas en 2021?*
  - *¿Cuál es el navegador más preferido por los clientes?*
- **Segmentación y Correlaciones:**
  - *¿Existe alguna diferencia en el gasto de compras entre hombres y mujeres?*
  - *¿Existe relación entre la edad del cliente y la venta total?*
  - *¿Los clientes suscritos al boletín compran más que los no suscritos?*
- **Generación de Gráficos:**
  - *Genera un gráfico de líneas con la tendencia de ventas por mes.*
  - *Crea un gráfico de barras con los métodos de pago más usados.*
  - *Genera un gráfico de dispersión entre la edad y la venta total.*
