#!/usr/bin/env python3
"""Genera las plantillas Excel de carga masiva (Odoo: Favoritos -> Importar registros).

  carga_masiva/datos_*.xlsx  -> exactamente lo que el seed ya cargó (documentación / Manual 1)
  carga_masiva/demo_*.xlsx   -> pocos registros NUEVOS para importar en vivo o tomar capturas

Los encabezados son nombres técnicos de Odoo 18, que el importador reconoce automáticamente.
Requiere openpyxl:  pip install openpyxl ;  python scripts/generar_carga_masiva.py
"""
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "seed"))
import data as D  # noqa: E402

OUT = os.path.join(ROOT, "carga_masiva")
COUNTRY = {"gt": "base.gt", "mx": "base.mx", "sv": "base.sv"}   # ID externo del país (no depende del idioma)
GREEN = PatternFill("solid", fgColor="007A4D")


def save(name, sheet, headers, rows, note):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    ws.append(headers)
    for r in rows:
        ws.append(list(r))
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = GREEN
        c.alignment = Alignment(horizontal="center")
    for i, h in enumerate(headers, start=1):
        width = max([len(str(h))] + [len(str(r[i - 1])) for r in rows if i - 1 < len(r)]) + 2
        ws.column_dimensions[get_column_letter(i)].width = min(width, 60)
    ws.freeze_panes = "A2"
    info = wb.create_sheet("LEEME")
    info.append(["Cómo importar en Odoo 18"])
    info["A1"].font = Font(bold=True, size=13)
    for line in note:
        info.append([line])
    info.column_dimensions["A"].width = 110
    wb.save(os.path.join(OUT, name))
    print(f"  {name}: {len(rows)} filas")


def main():
    os.makedirs(OUT, exist_ok=True)
    common = ["IMPORTANTE: los archivos datos_*.xlsx ya están cargados por el seed (si se importan otra vez Odoo",
              "marcará duplicados). Para capturas/demostración en vivo usar los demo_*.xlsx (registros nuevos).",
              "1. Abrir el menú indicado abajo y la vista de lista.",
              "2. Ícono de engrane (⚙) o 'Favoritos' -> 'Importar registros' -> 'Subir archivo'.",
              "3. Verificar que cada columna quede emparejada con su campo -> 'Probar' -> 'Importar'.",
              "Los campos relacionados (departamento, cargo, categoría, país) se emparejan por NOMBRE."]

    # ---------------- Departamentos
    deps = [(n,) for _c, n in D.DEPARTMENTS]
    save("datos_departamentos.xlsx", "Departamentos", ["name"], deps, common + ["Menú: Empleados -> Departamentos"])
    save("demo_departamentos.xlsx", "Departamentos", ["name"], [("Control de Calidad",)],
         common + ["Menú: Empleados -> Departamentos", "Registro NUEVO (no existe en la base)."])

    # ---------------- Cargos
    dep_name = dict(D.DEPARTMENTS)
    jobs = [(n, dep_name[d], desc) for n, d, _w, desc in D.JOBS.values()]
    save("datos_cargos.xlsx", "Cargos", ["name", "department_id", "description"], jobs,
         common + ["Menú: Empleados -> Configuración -> Puestos de trabajo"])
    save("demo_cargos.xlsx", "Cargos", ["name", "department_id", "description"],
         [("Supervisor de Calidad", "Operaciones de Sucursal", "Verifica la calidad y el estado de los productos antes de ponerlos a la venta.")],
         common + ["Menú: Empleados -> Configuración -> Puestos de trabajo", "Registro NUEVO."])

    # ---------------- Empleados
    hdr = ["name", "job_id", "job_title", "department_id", "work_location_id", "work_email", "work_phone"]
    emps = []
    for name, job, br, _g in D.EMPLOYEES:
        jname, dep, _w, _ = D.JOBS[job]
        import unicodedata
        p = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower().split()
        email = f"{p[0]}.{p[-2] if len(p) >= 3 else p[-1]}@quetzalmart.gt"
        emps.append((name, jname, jname, dep_name[dep], D.BRANCHES[br][0], email, D.BRANCHES[br][5]))
    save("datos_empleados.xlsx", "Empleados", hdr, emps, common + ["Menú: Empleados -> Empleados"])
    save("demo_empleados.xlsx", "Empleados", hdr, [
        ("Lucía Fernanda Batres Cano", "Bodeguero", "Bodeguero", "Compras y Logística", D.BRANCHES["GT"][0], "lucia.batres@quetzalmart.gt", D.BRANCHES["GT"][5]),
        ("Mario Alberto Santizo Lux", "Cajero", "Cajero", "Operaciones de Sucursal", D.BRANCHES["GT"][0], "mario.santizo@quetzalmart.gt", D.BRANCHES["GT"][5]),
        ("Elena Patricia Rosales Díaz", "Ejecutivo de Ventas", "Ejecutivo de Ventas", "Ventas y Atención al Cliente", D.BRANCHES["SV"][0], "elena.rosales@quetzalmart.gt", D.BRANCHES["SV"][5]),
    ], common + ["Menú: Empleados -> Empleados", "Registros NUEVOS."])

    # ---------------- Proveedores
    hdr = ["name", "is_company", "vat", "street", "city", "country_id/id", "phone", "email", "supplier_rank", "category_id"]
    vend = [(n, True, vat, st, city, COUNTRY[c], ph, em, 1, "Proveedor") for n, vat, c, city, st, ph, em, _cats in D.VENDORS]
    vend += [(n, True, vat, st, city, COUNTRY[c], ph, em, 1, "Proveedor,Outsourcing")
             for n, vat, c, city, st, ph, em, _code, _s, _p in D.OUTSOURCING_VENDORS]
    save("datos_proveedores.xlsx", "Proveedores", hdr, vend, common + ["Menú: Compras -> Pedidos -> Proveedores (vista lista)",
         "country_id/id usa el ID externo del país: base.gt, base.mx, base.sv."])
    save("demo_proveedores.xlsx", "Proveedores", hdr, [
        ("Distribuidora de Empaques Petén, S.A.", True, "4433221-0", "Calle Principal 3-15", "Flores", "base.gt", "+502 7926 1100", "ventas@empapeten.example.com", 1, "Proveedor"),
        ("Suministros Industriales Izalco, S.A. de C.V.", True, "0315-200780-101-4", "Carretera a Sonsonate Km 62", "Izalco", "base.sv", "+503 2453 2200", "ventas@sizalco.example.com", 1, "Proveedor"),
    ], common + ["Menú: Compras -> Pedidos -> Proveedores", "Registros NUEVOS."])

    # ---------------- Materiales
    hdr = ["default_code", "name", "categ_id", "type", "is_storable", "sale_ok", "purchase_ok",
           "standard_price", "list_price", "seller_ids/partner_id", "seller_ids/price"]
    vend_by_cat = {}
    for n, _vat, _c, _city, _st, _ph, _em, cats in D.VENDORS:
        for c in cats:
            vend_by_cat.setdefault(c, n)
    counters, mats = {}, []
    for cat, name, cost in D.MATERIALS:
        counters[cat] = counters.get(cat, 0) + 1
        mats.append((f"MAT-{cat}-{counters[cat]:02d}", name, f"{D.MATERIAL_ROOT} / {D.MATERIAL_CATEGORIES[cat]}",
                     "consu", True, False, True, cost, round(cost * 1.35, 2), vend_by_cat[cat], cost))
    save("datos_materiales.xlsx", "Materiales", hdr, mats,
         common + ["Menú: Compras -> Productos -> Productos (vista lista)",
                   "type = consu (Bienes) + is_storable = Verdadero -> se controla inventario.",
                   "seller_ids/partner_id y seller_ids/price crean el proveedor del producto."])
    save("demo_materiales.xlsx", "Materiales", hdr, [
        ("MAT-LIM-09", "Atomizador plástico 1 L", f"{D.MATERIAL_ROOT} / Limpieza e Higiene", "consu", True, False, True, 14.0, 18.9, "Distribuidora Limpiamax, S.A.", 14.0),
        ("MAT-EMP-09", "Bolsa térmica para congelados (paquete 100)", f"{D.MATERIAL_ROOT} / Empaque y Bolsas", "consu", True, False, True, 120.0, 162.0, "Empaques Centroamericanos, S.A.", 120.0),
        ("MAT-POS-09", "Lector de tarjetas NFC para POS", f"{D.MATERIAL_ROOT} / Equipo de Punto de Venta", "consu", True, False, True, 950.0, 1282.5, "Tecnología POS Guatemala, S.A.", 950.0),
        ("MAT-REF-09", "Cortina de aire para puerta 90 cm", f"{D.MATERIAL_ROOT} / Refrigeración y Exhibición", "consu", True, False, True, 2100.0, 2835.0, "Refrigeración Comercial del Pacífico, S.A.", 2100.0),
    ], common + ["Menú: Compras -> Productos -> Productos", "Registros NUEVOS."])
    print(f"Plantillas en {OUT}")


if __name__ == "__main__":
    main()
