"""Generacion de graficos variados (Integrante 4 - Correlaciones y Graficos).

Genera al menos 7 graficos (lineas, barras, barras horizontales, pastel,
histograma, dispersion, cajas y barras agrupadas) a partir de la vista
consolidada `ventas.vw_ventas` y los guarda en la carpeta `graficas/`.

Uso:
    python graficas.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from conexion import obtener_engine

DIRECTORIO_SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficas")

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


def cargar_datos() -> pd.DataFrame:
    engine = obtener_engine()
    consulta = "SELECT * FROM ventas.vw_ventas;"
    df = pd.read_sql(consulta, engine)
    if df.empty:
        raise RuntimeError("La vista ventas.vw_ventas no devolvio datos.")
    return df


def guardar(fig, nombre: str) -> str:
    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)
    ruta = os.path.join(DIRECTORIO_SALIDA, nombre)
    fig.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return ruta


def grafico_tendencia_mensual(df: pd.DataFrame) -> str:
    ventas_mes = (
        df.groupby("mes_compra")["monto_compra"]
        .sum()
        .reset_index()
        .sort_values("mes_compra")
    )
    ventas_mes["mes"] = ventas_mes["mes_compra"].map(MESES)

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.lineplot(
        data=ventas_mes,
        x="mes",
        y="monto_compra",
        marker="o",
        linewidth=2.5,
        color="#2b5c8f",
        ax=ax,
    )
    ax.set_title("Tendencia de Ventas por Mes (2021)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Mes", fontsize=11, fontweight="bold")
    ax.set_ylabel("Monto Total (Q)", fontsize=11, fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return guardar(fig, "tendencia_ventas_mes.png")


def grafico_ventas_metodo_pago(df: pd.DataFrame) -> str:
    ventas_metodo = (
        df.groupby("metodo_pago")["monto_compra"]
        .sum()
        .reset_index()
        .sort_values("monto_compra", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=ventas_metodo,
        x="metodo_pago",
        y="monto_compra",
        hue="metodo_pago",
        palette="crest",
        legend=False,
        ax=ax,
    )
    ax.set_title("Ventas por Metodo de Pago", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Metodo de Pago", fontsize=11, fontweight="bold")
    ax.set_ylabel("Monto Total (Q)", fontsize=11, fontweight="bold")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    return guardar(fig, "ventas_metodo_pago.png")


def grafico_compras_navegador(df: pd.DataFrame) -> str:
    compras_navegador = df["navegador"].value_counts().reset_index()
    compras_navegador.columns = ["navegador", "cantidad"]
    compras_navegador = compras_navegador.sort_values("cantidad", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=compras_navegador,
        x="cantidad",
        y="navegador",
        hue="navegador",
        palette="mako",
        legend=False,
        ax=ax,
    )
    ax.set_title("Cantidad de Compras por Navegador", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Cantidad de Compras", fontsize=11, fontweight="bold")
    ax.set_ylabel("Navegador", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, "compras_navegador.png")


def grafico_distribucion_genero(df: pd.DataFrame) -> str:
    distribucion = df["genero"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        distribucion.values,
        labels=distribucion.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("pastel"),
        textprops={"fontsize": 12},
    )
    ax.set_title("Distribucion de Compras por Genero", fontsize=14, fontweight="bold", pad=20)
    fig.tight_layout()
    return guardar(fig, "distribucion_genero.png")


def grafico_histograma_edades(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x="edad", bins=20, kde=True, color="#3498db", ax=ax)
    ax.set_title("Distribucion de Edad de los Clientes", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Edad (anios)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Frecuencia", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, "histograma_edades.png")


def grafico_dispersion_monto_tiempo(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x="tiempo_sitio",
        y="monto_compra",
        color="#e74c3c",
        s=40,
        alpha=0.6,
        ax=ax,
    )
    ax.set_title("Monto de Compra vs Tiempo en el Sitio", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Tiempo en el Sitio (segundos)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Monto de Compra (Q)", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, "dispersion_monto_tiempo.png")


def grafico_cajas_venta_genero(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.boxplot(
        data=df, x="genero", y="venta_total",
        hue="genero", palette="Set2", legend=False, ax=ax,
    )
    ax.set_title("Venta Total por Genero", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Genero", fontsize=11, fontweight="bold")
    ax.set_ylabel("Venta Total (Q)", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, "cajas_venta_genero.png")


def grafico_promociones(df: pd.DataFrame) -> str:
    df = df.copy()
    df["boletin"] = df["boletin"].map({True: "Con Boletín", False: "Sin Boletín"})
    df["vale"] = df["vale"].map({True: "Con Vale", False: "Sin Vale"})

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df,
        x="boletin",
        y="monto_compra",
        hue="vale",
        palette="rocket",
        ax=ax,
    )
    ax.set_title("Ventas por Uso de Boletin y Vale", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Uso de Boletin", fontsize=11, fontweight="bold")
    ax.set_ylabel("Monto Total (Q)", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, "ventas_promociones.png")


def generar_todas_las_graficas() -> list[str]:
    df = cargar_datos()
    sns.set_theme(style="whitegrid")

    generadores = [
        grafico_tendencia_mensual,
        grafico_ventas_metodo_pago,
        grafico_compras_navegador,
        grafico_distribucion_genero,
        grafico_histograma_edades,
        grafico_dispersion_monto_tiempo,
        grafico_cajas_venta_genero,
        grafico_promociones,
    ]

    rutas = []
    for generador in generadores:
        ruta = generador(df)
        rutas.append(ruta)
        print(f"Grafico guardado: {ruta}")

    print(f"\nTotal de graficos generados: {len(rutas)}")
    return rutas


if __name__ == "__main__":
    try:
        generar_todas_las_graficas()
    except Exception as exc:
        print(f"Error al generar las graficas: {exc}")
        raise
