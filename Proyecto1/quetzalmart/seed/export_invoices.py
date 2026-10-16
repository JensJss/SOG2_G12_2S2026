#!/usr/bin/env python3
"""Exporta a PDF todas las facturas publicadas (compras y ventas) de Odoo.

Estructura de salida:
  facturas_pdf/
    compras/  FACTURA_PROVEEDOR_<numero>__<proveedor>.pdf
    ventas/   FACTURA_CLIENTE_<numero>__<cliente>.pdf
    indice_facturas.csv

Solo descarga las que todavía no existen en la carpeta, así que se puede volver
a correr durante la calificación para agregar las facturas recién generadas
(rúbrica 1.09):
    docker compose --profile seed run --rm --entrypoint python3 seed -u /seed/export_invoices.py
"""
import csv
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qm_rpc import Odoo, env  # noqa: E402

REPORT = "account.report_invoice_with_payments"
FOLDERS = {"in_invoice": "compras", "in_refund": "compras", "out_invoice": "ventas", "out_refund": "ventas"}
PREFIX = {"in_invoice": "FACTURA_PROVEEDOR", "in_refund": "NC_PROVEEDOR",
          "out_invoice": "FACTURA_CLIENTE", "out_refund": "NC_CLIENTE"}


def safe(text, maxlen=60):
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return text[:maxlen]


def export_all(o, out_dir, force=False):
    os.makedirs(out_dir, exist_ok=True)
    moves = o.search_read("account.move",
                          [("move_type", "in", list(FOLDERS)), ("state", "=", "posted")],
                          ["name", "move_type", "partner_id", "invoice_date", "amount_total", "currency_id",
                           "payment_state", "ref", "invoice_origin"],
                          order="move_type, invoice_date, name")
    opener = o.http_session()
    new = 0
    rows = []
    for m in moves:
        folder = os.path.join(out_dir, FOLDERS[m["move_type"]])
        os.makedirs(folder, exist_ok=True)
        partner = m["partner_id"][1] if m["partner_id"] else "sin_contacto"
        fname = f"{PREFIX[m['move_type']]}_{safe(m['name'], 40)}__{safe(partner, 40)}.pdf"
        path = os.path.join(folder, fname)
        if force or not os.path.exists(path):
            with opener.open(f"{o.url}/report/pdf/{REPORT}/{m['id']}", timeout=180) as r:
                content = r.read()
            if not content.startswith(b"%PDF"):
                raise RuntimeError(f"La respuesta para {m['name']} no es un PDF (¿wkhtmltopdf/report.url?)")
            with open(path, "wb") as f:
                f.write(content)
            new += 1
            if new % 20 == 0:
                print(f"  {new} PDFs nuevos...", flush=True)
        rows.append([m["name"], m["move_type"], partner, m["invoice_date"], m["ref"] or "", m["invoice_origin"] or "",
                     f"{m['amount_total']:.2f}", m["currency_id"][1], m["payment_state"],
                     os.path.relpath(path, out_dir)])
    with open(os.path.join(out_dir, "indice_facturas.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["numero", "tipo", "contacto", "fecha", "referencia", "origen", "total", "moneda", "estado_pago", "archivo"])
        w.writerows(rows)
    print(f"PDFs de facturas: {len(rows)} en total ({new} nuevos) -> {out_dir}", flush=True)
    return len(rows)


if __name__ == "__main__":
    out = env("PDF_OUT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "facturas_pdf"))
    odoo = Odoo(env("ODOO_URL", "http://localhost:18069"), env("ODOO_DB", "quetzalmart"),
                env("ODOO_ADMIN_LOGIN", "admin"), env("ODOO_ADMIN_PASSWORD")).connect()
    export_all(odoo, out, force="--force" in sys.argv)
