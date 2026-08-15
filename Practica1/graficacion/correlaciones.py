"""Estudio de correlaciones (Integrante 4 - Correlaciones y Graficos).

Genera graficos de correlacion y los guarda en la carpeta `graficas/`:
  - Edad vs Venta_total (dispersión con linea de regresion y coeficiente r).
  - Genero vs Metodo de Pago (tabla cruzada de frecuencias).
  - Boletin vs Vale (tabla cruzada de frecuencias).
  - Matriz de correlacion de las variables numericas (heatmap).

Uso:
    python correlaciones.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from conexion import obtener_engine

DIRECTORIO_SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graficas")

VARIABLES_NUMERICAS = ["edad", "venta_total", "n_compras", "monto_compra", "tiempo_sitio"]


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


def correlacion_edad_venta_total(df: pd.DataFrame) -> str:
    r = df["edad"].corr(df["venta_total"])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(
        data=df,
        x="edad",
        y="venta_total",
        scatter_kws={"s": 30, "alpha": 0.5, "color": "#e74c3c"},
        line_kws={"color": "#2b5c8f", "linewidth": 2},
        ax=ax,
    )
    ax.set_title(f"Correlacion: Edad vs Venta Total  (r = {r:.4f})",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Edad (anios)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Venta Total (Q)", fontsize=11, fontweight="bold")
    ax.annotate(
        f"Coeficiente de Pearson (r) = {r:.4f}",
        xy=(0.03, 0.95),
        xycoords="axes fraction",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#2b5c8f", alpha=0.9),
    )
    fig.tight_layout()
    return guardar(fig, "correlacion_edad_venta_total.png")


def correlacion_genero_metodo_pago(df: pd.DataFrame) -> str:
    cruzada = pd.crosstab(df["genero"], df["metodo_pago"])

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        cruzada,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        cbar_kws={"label": "Cantidad de Compras"},
        ax=ax,
    )
    ax.set_title("Correlacion: Genero vs Metodo de Pago", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Metodo de Pago", fontsize=11, fontweight="bold")
    ax.set_ylabel("Genero", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, "correlacion_genero_metodo_pago.png")


def correlacion_boletin_vale(df: pd.DataFrame) -> str:
    df = df.copy()
    df["boletin"] = df["boletin"].map({True: "Con Boletín", False: "Sin Boletín"})
    df["vale"] = df["vale"].map({True: "Con Vale", False: "Sin Vale"})
    cruzada = pd.crosstab(df["boletin"], df["vale"])

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cruzada,
        annot=True,
        fmt="d",
        cmap="crest",
        cbar_kws={"label": "Cantidad de Compras"},
        ax=ax,
    )
    ax.set_title("Correlacion: Uso de Boletin vs Uso de Vale", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Uso de Vale", fontsize=11, fontweight="bold")
    ax.set_ylabel("Uso de Boletin", fontsize=11, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, "correlacion_boletin_vale.png")


def matriz_correlaciones(df: pd.DataFrame) -> str:
    matriz = df[VARIABLES_NUMERICAS].corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        matriz,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        cbar_kws={"label": "Coeficiente de Pearson"},
        ax=ax,
    )
    ax.set_title("Matriz de Correlacion de Variables Numericas",
                 fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    return guardar(fig, "matriz_correlaciones.png")


def generar_todas_las_correlaciones() -> list[str]:
    df = cargar_datos()
    sns.set_theme(style="whitegrid")

    print("Correlaciones calculadas:")
    print(f"  Edad vs Venta_total:      r = {df['edad'].corr(df['venta_total']):.4f}")
    print(f"  Monto_compra vs Tiempo:   r = {df['monto_compra'].corr(df['tiempo_sitio']):.4f}")
    print(f"  Venta_total vs N_compras: r = {df['venta_total'].corr(df['n_compras']):.4f}")

    generadores = [
        correlacion_edad_venta_total,
        correlacion_genero_metodo_pago,
        correlacion_boletin_vale,
        matriz_correlaciones,
    ]

    rutas = []
    for generador in generadores:
        ruta = generador(df)
        rutas.append(ruta)
        print(f"Grafico guardado: {ruta}")

    print(f"\nTotal de graficos de correlacion generados: {len(rutas)}")
    return rutas


if __name__ == "__main__":
    try:
        generar_todas_las_correlaciones()
    except Exception as exc:
        print(f"Error al generar las correlaciones: {exc}")
        raise
