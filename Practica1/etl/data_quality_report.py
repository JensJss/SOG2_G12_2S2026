"""
SOG2 - Practica 1 - Segundo Semestre 2026
Reporte de Calidad de Datos (evidencia para el informe)

No modifica ni carga nada: solo audita el CSV de origen y deja un resumen
en consola (y opcionalmente en un .md) de las validaciones aplicadas por
el ETL (etl.py), como evidencia de que el proceso de limpieza fue
verificado de forma rigurosa.

Uso:
    python data_quality_report.py
    python data_quality_report.py --out reporte_calidad.md
"""

import argparse
import os

import pandas as pd

CSV_POR_DEFECTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Venta_online_c.csv")

GENERO_VALIDOS = {0, 1}
METODO_PAGO_VALIDOS = {0, 1, 2}
NAVEGADOR_VALIDOS = {0, 1, 2, 3, 4}
BOOL_VALIDOS = {0, 1}


def auditar(csv_path: str) -> list[tuple[str, str, str]]:
    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
    fechas = pd.to_datetime(df["FechaCompra"], format="%d.%m.%y", errors="coerce")

    filas = []

    def check(nombre, resultado, esperado="0"):
        estado = "OK" if str(resultado) == esperado else "REVISAR"
        filas.append((nombre, str(resultado), estado))

    check("Total de filas leidas", len(df), esperado=str(len(df)))
    check("Valores nulos (total en todas las columnas)", int(df.isnull().sum().sum()))
    check("Filas duplicadas (exactas)", int(df.duplicated().sum()))
    check("Id_cliente duplicados", int(df.duplicated(subset=["Id_cliente"]).sum()))
    check("Genero fuera de dominio {0,1}", int((~df["Genero"].isin(GENERO_VALIDOS)).sum()))
    check("MetodoPago fuera de dominio {0,1,2}", int((~df["MetodoPago"].isin(METODO_PAGO_VALIDOS)).sum()))
    check("Navegador fuera de dominio {0..4}", int((~df["Navegador"].isin(NAVEGADOR_VALIDOS)).sum()))
    check("Boletin fuera de dominio {0,1}", int((~df["Boletin"].isin(BOOL_VALIDOS)).sum()))
    check("Vale fuera de dominio {0,1}", int((~df["Vale"].isin(BOOL_VALIDOS)).sum()))
    check("Fechas invalidas / no parseables (formato DD.MM.YY)", int(fechas.isna().sum()))
    check("Fechas fuera del anio 2021", int((fechas.dt.year != 2021).sum()))
    check("Edad fuera de rango [0,120]", int((~df["Edad"].between(0, 120)).sum()))
    check("Venta_total <= 0", int((df["Venta_total"] <= 0).sum()))
    check("MontoCompra <= 0", int((df["MontoCompra"] <= 0).sum()))
    check("Tiempo <= 0", int((df["Tiempo"] <= 0).sum()))
    check("N_Compras = 0 pero Venta_total > 0 (inconsistencia)",
          int(((df["N_Compras"] == 0) & (df["Venta_total"] > 0)).sum()))
    check("MontoCompra > Venta_total (inconsistencia)",
          int((df["MontoCompra"] > df["Venta_total"]).sum()))

    return filas


def imprimir(filas):
    ancho1 = max(len(f[0]) for f in filas) + 2
    print(f"{'Validacion':<{ancho1}}{'Resultado':<12}{'Estado'}")
    print("-" * (ancho1 + 20))
    for nombre, resultado, estado in filas:
        print(f"{nombre:<{ancho1}}{resultado:<12}{estado}")


def a_markdown(filas) -> str:
    md = ["| Validación | Resultado | Estado |", "|---|---|---|"]
    for nombre, resultado, estado in filas:
        icono = "✅" if estado == "OK" else "⚠️"
        md.append(f"| {nombre} | {resultado} | {icono} {estado} |")
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="Reporte de calidad de datos del CSV de origen")
    parser.add_argument("--csv", default=CSV_POR_DEFECTO, help="Ruta al CSV (default: junto a este script)")
    parser.add_argument("--out", default=None, help="Ruta opcional para guardar el reporte en Markdown")
    args = parser.parse_args()

    filas = auditar(args.csv)
    imprimir(filas)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("# Reporte de Calidad de Datos - Venta_online_c.csv\n\n")
            f.write(a_markdown(filas))
            f.write("\n")
        print(f"\nReporte guardado en: {args.out}")


if __name__ == "__main__":
    main()
