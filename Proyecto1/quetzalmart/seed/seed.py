#!/usr/bin/env python3
"""Carga inicial de QuetzalMart en Odoo 18 Community (Integrante 3).

Hace, en orden y de forma IDEMPOTENTE (se puede correr varias veces):
  1. Crea la base (es_419, país Guatemala, GTQ) si no existe.
  2. Instala los módulos base de TODO el equipo.
  3. Configura la empresa, logo, 3 sucursales (almacenes GT / MX / SV).
  4. RR. HH.: 5 departamentos, 8 cargos, 36 empleados + contratos.
  5. Proveedores (16 de materiales + 4 de outsourcing).
  6. 64 materiales para el funcionamiento de las sucursales (+4 servicios).
  7. 105 compras confirmadas -> recibidas -> facturadas -> 80 % pagadas
     + 12 solicitudes de cotización a proveedores.
  8. Exporta los PDF de todas las facturas a ./facturas_pdf

Uso con Docker:   docker compose --profile seed run --rm seed
Uso sin Docker:   ODOO_URL=http://localhost:18069 ODOO_ADMIN_PASSWORD=... python seed/seed.py
Opciones:         SEED_SKIP_PDF=1  (no exportar PDFs)
"""
import base64
import io
import os
import random
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data as D  # noqa: E402
from qm_rpc import Odoo, env, wait_for_odoo  # noqa: E402

URL = env("ODOO_URL", "http://localhost:18069")
DB = env("ODOO_DB", "quetzalmart")
MASTER = env("ODOO_MASTER_PASSWORD", "")
LOGIN = env("ODOO_ADMIN_LOGIN", "admin")
PASSWORD = env("ODOO_ADMIN_PASSWORD")
PUBLIC_URL = env("ODOO_PUBLIC_URL", URL)
# URL que usa wkhtmltopdf DENTRO del contenedor de Odoo para cargar CSS/logo de los PDF
REPORT_URL = env("ODOO_REPORT_URL", "http://localhost:8069")
PDF_OUT = env("PDF_OUT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "facturas_pdf"))

MODULES = [
    # Integrante 3 (ERP administrativo)
    "contacts", "hr", "hr_contract", "purchase", "purchase_stock", "stock", "account",
    # Integrante 4 (portal web, ventas, CRM, marketing)
    "sale_management", "sale_stock", "crm", "website", "website_sale", "website_sale_stock",
    "mass_mailing", "mass_mailing_sale", "mass_mailing_crm", "base_automation",
    # Integrante 1 (gestor documental OCA)
    "dms",
]

SEED_ORIGIN = "QM-SEED"
SEED_RFQ_ORIGIN = "QM-SEED-RFQ"

rng = random.Random(D.RANDOM_SEED)


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def rand_date(d_from=D.DATE_FROM, d_to=D.DATE_TO, r=None):
    r = r or rng
    a = date.fromisoformat(d_from)
    b = date.fromisoformat(d_to)
    return a + timedelta(days=r.randint(0, (b - a).days))


def dt(d, hour=None, r=None):
    """Fecha/hora en UTC (Guatemala = UTC-6): 14-22 h UTC = 8-16 h local."""
    r = r or rng
    return datetime(d.year, d.month, d.day, hour if hour is not None else r.randint(14, 22), r.randint(0, 59)).strftime("%Y-%m-%d %H:%M:%S")


# ============================================================================ 1. BASE
def ensure_database():
    wait_for_odoo(URL)
    db = Odoo.proxy(URL, "db")
    if db.db_exist(DB):
        log(f"Base '{DB}' ya existe.")
        return False
    if not MASTER:
        raise SystemExit("ODOO_MASTER_PASSWORD es necesario para crear la base.")
    log(f"Creando base '{DB}' (es_419, Guatemala). Tarda 1-3 min...")
    db.create_database(MASTER, DB, False, "es_419", PASSWORD, LOGIN, "gt", D.COMPANY["phone"])
    log("Base creada.")
    return True


# ============================================================================ 2. MÓDULOS
def install_modules(o):
    o.call("ir.module.module", "update_list")
    mods = o.search_read("ir.module.module", [("name", "in", MODULES)], ["name", "state"])
    found = {m["name"] for m in mods}
    missing = set(MODULES) - found
    if missing:
        log(f"ADVERTENCIA: módulos no encontrados en addons_path: {sorted(missing)}")
    to_install = [m["id"] for m in mods if m["state"] != "installed"]
    if to_install:
        names = [m["name"] for m in mods if m["state"] != "installed"]
        log(f"Instalando {len(names)} módulos: {', '.join(names)} (puede tardar 5-10 min)...")
        o.call("ir.module.module", "button_immediate_install", to_install)
        o._fields_cache.clear()
        log("Módulos instalados.")
    else:
        log("Módulos ya instalados.")
    # l10n_gt se instala automáticamente con account porque la empresa es de Guatemala
    l10n = o.search_read("ir.module.module", [("name", "=", "l10n_gt")], ["state"])
    log(f"Localización contable l10n_gt: {l10n[0]['state'] if l10n else 'no encontrada'}")


# ============================================================================ 3. EMPRESA
def make_logo_png():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return False
    img = Image.new("RGBA", (360, 120), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((6, 6, 114, 114), fill=(0, 122, 77, 255))
    d.polygon([(60, 24), (92, 60), (60, 96), (28, 60)], fill=(255, 196, 0, 255))
    font_big = font_small = None
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(path):
            font_big = ImageFont.truetype(path, 40)
            font_small = ImageFont.truetype(path, 16)
            break
    font_big = font_big or ImageFont.load_default()
    font_small = font_small or ImageFont.load_default()
    d.text((128, 22), "Quetzal", fill=(0, 122, 77, 255), font=font_big)
    d.text((128, 64), "Mart", fill=(230, 160, 0, 255), font=font_big)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def country_id(o, code):
    return o.search("res.country", [("code", "=", code.upper())], limit=1)[0]


def setup_company(o):
    company_id = o.search("res.company", [], limit=1, order="id")[0]
    vals = dict(D.COMPANY)
    vals["country_id"] = country_id(o, "gt")
    gtq = o.search("res.currency", [("name", "=", "GTQ")], limit=1)
    logo = make_logo_png()
    if logo:
        vals["logo"] = logo
    # Diseño de documentos (encabezado con logo en facturas/órdenes de compra PDF)
    layout_view = o.ref("web.external_layout_boxed", raise_if_not_found=False)
    if layout_view:
        vals["external_report_layout_id"] = layout_view
    vals.update({
        "primary_color": "#007A4D", "secondary_color": "#E6A000",
        "report_header": "Precios accesibles para todos · Guatemala · México · El Salvador",
        "report_footer": f"{D.COMPANY['name']} · NIT {D.COMPANY['vat']} · {D.COMPANY['phone']} · {D.COMPANY['email']}",
    })
    o.write("res.company", company_id, vals)
    comp = o.search_read("res.company", [("id", "=", company_id)], ["currency_id", "partner_id"])[0]
    log(f"Empresa configurada: {D.COMPANY['name']} | moneda {comp['currency_id'][1]}")
    if gtq and comp["currency_id"][0] != gtq[0]:
        log("ADVERTENCIA: la moneda de la empresa no es GTQ.")
    # zona horaria / idioma del admin
    o.write("res.users", o.uid, {"name": "Administrador QuetzalMart", "tz": "America/Guatemala", "lang": "es_419",
                                 "email": "admin@quetzalmart.gt"})
    # URLs: web.base.url público y report.url interno (wkhtmltopdf dentro del contenedor)
    ICP = "ir.config_parameter"
    o.call(ICP, "set_param", "web.base.url", PUBLIC_URL)
    o.call(ICP, "set_param", "web.base.url.freeze", "True")
    o.call(ICP, "set_param", "report.url", REPORT_URL)
    return company_id, comp["partner_id"][0]


def enable_settings(o):
    vals = o.clean("res.config.settings", {
        "group_stock_multi_warehouses": True,
        "group_stock_multi_locations": True,
        "group_product_variant": True,
        "group_uom": True,
    })
    sid = o.call("res.config.settings", "create", vals)
    o.call("res.config.settings", "execute", [sid])
    log("Ajustes: multi-almacén, ubicaciones, variantes y UdM activados.")


def setup_branches(o, company_partner_id):
    branches = {}
    wh_ids = o.search("stock.warehouse", [], order="id")
    for key, (name, code, ctry, city, street, phone) in D.BRANCHES.items():
        if key == "GT":
            partner_id = company_partner_id
            wid = wh_ids[0]
            o.write("stock.warehouse", wid, {"name": name, "code": code})
        else:
            partner_id, _ = o.get_or_create("res.partner", [("name", "=", f"QuetzalMart Sucursal {city.split(',')[0]}")], {
                "name": f"QuetzalMart Sucursal {city.split(',')[0]}", "is_company": True,
                "street": street, "city": city, "country_id": country_id(o, ctry), "phone": phone,
                "parent_id": company_partner_id, "type": "other",
            })
            found = o.search("stock.warehouse", [("code", "=", code)], limit=1)
            if found:
                wid = found[0]
            else:
                wid = o.create("stock.warehouse", {"name": name, "code": code, "partner_id": partner_id})
        wh = o.search_read("stock.warehouse", [("id", "=", wid)], ["in_type_id", "lot_stock_id"])[0]
        loc_id, _ = o.get_or_create("hr.work.location", [("name", "=", name)], {
            "name": name, "address_id": partner_id, "location_type": "office"})
        branches[key] = {"warehouse_id": wid, "in_type_id": wh["in_type_id"][0], "partner_id": partner_id,
                         "work_location_id": loc_id, "name": name, "country": ctry}
    log(f"Sucursales/almacenes: {', '.join(b['name'] for b in branches.values())}")
    return branches


# ============================================================================ 4. RR. HH.
def slug_email(name):
    import unicodedata
    parts = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower().split()
    return f"{parts[0]}.{parts[-2] if len(parts) >= 3 else parts[-1]}@quetzalmart.gt"


def setup_hr(o, branches):
    # Odoo crea "Administración" por defecto: se reutiliza como Dirección General (quedan 5 exactos)
    dir_name = dict(D.DEPARTMENTS)["DIR"]
    default_dep = o.ref("hr.dep_administration", raise_if_not_found=False)
    if default_dep and not o.search("hr.department", [("name", "=", dir_name)]):
        o.write("hr.department", default_dep, {"name": dir_name})
    if default_dep:
        # el nombre es traducible: se fija también en es_419 (si no, la UI sigue mostrando "Administración")
        o.call("hr.department", "write", [default_dep], {"name": dir_name}, context={"lang": "es_419"})
    dept_ids = {}
    for code, name in D.DEPARTMENTS:
        dept_ids[code], _ = o.get_or_create("hr.department", [("name", "=", name)], {"name": name})
    job_ids = {}
    for key, (name, dept, _wage, desc) in D.JOBS.items():
        job_ids[key], _ = o.get_or_create("hr.job", [("name", "=", name)], {
            "name": name, "department_id": dept_ids[dept], "description": f"<p>{desc}</p>",
            "no_of_recruitment": 1 if key in ("CAJ", "BOD", "EV") else 0})
    emp_ids = {}
    used_emails = set()
    for i, (name, job, branch, gender) in enumerate(D.EMPLOYEES):
        jname, dept, _wage, _ = D.JOBS[job]
        email = slug_email(name)
        while email in used_emails:
            email = email.replace("@", f"{i}@")
        used_emails.add(email)
        b = branches[branch]
        prefix = {"GT": "+502 5", "MX": "+52 962 1", "SV": "+503 7"}[branch]
        birth = date(1975 + (i * 7) % 26, 1 + (i * 5) % 12, 1 + (i * 11) % 28)
        vals = {
            "name": name,
            "job_id": job_ids[job],
            "job_title": jname,
            "department_id": dept_ids[dept],
            "work_email": email,
            "work_phone": D.BRANCHES[branch][5],
            "mobile_phone": f"{prefix}{rng.randint(100, 999)} {rng.randint(1000, 9999)}",
            "work_location_id": b["work_location_id"],
            "address_id": b["partner_id"],
            "gender": gender,
            "sex": gender,
            "birthday": birth.isoformat(),
            "identification_id": f"{rng.randint(1000, 3999)} {rng.randint(10000, 99999)} {rng.randint(101, 2299):04d}",
            "private_city": D.BRANCHES[branch][3],
            "private_country_id": country_id(o, D.BRANCHES[branch][2]),
            "country_id": country_id(o, D.BRANCHES[branch][2]),
            "employee_type": "employee",
        }
        emp_ids[name], _ = o.get_or_create("hr.employee", [("name", "=", name)], vals)

    # Jefes de departamento y jerarquía
    for code, mgr in D.DEPARTMENT_MANAGERS.items():
        o.write("hr.department", dept_ids[code], {"manager_id": emp_ids[mgr]})
    gg = emp_ids[D.DEPARTMENT_MANAGERS["DIR"]]
    branch_mgr = {br: emp_ids[n] for n, j, br, _ in D.EMPLOYEES if j == "GS"}
    for name, job, branch, _ in D.EMPLOYEES:
        if job == "GG":
            parent = False
        elif job == "GS":
            parent = gg
        elif job in ("CAJ", "BOD", "EV") or (branch != "GT"):
            parent = branch_mgr[branch]
        else:
            parent = emp_ids[D.DEPARTMENT_MANAGERS[D.JOBS[job][1]]]
            if parent == emp_ids[name]:
                parent = gg
        o.write("hr.employee", emp_ids[name], {"parent_id": parent, "coach_id": parent})

    # El empleado ligado al usuario admin (lo crea Odoo) se ubica en Dirección
    admin_emp = o.search("hr.employee", [("user_id", "=", o.uid)], limit=1)
    if admin_emp:
        o.write("hr.employee", admin_emp, {"department_id": dept_ids["DIR"], "parent_id": gg,
                                           "job_title": "Administrador del Sistema ERP",
                                           "work_location_id": branches["GT"]["work_location_id"]})

    # Contratos (hr_contract)
    if o.count("ir.model", [("model", "=", "hr.contract")]):
        for idx, (name, job, branch, _) in enumerate(D.EMPLOYEES):
            eid = emp_ids[name]
            if o.count("hr.contract", [("employee_id", "=", eid)]):
                continue
            jname, dept, wage, _ = D.JOBS[job]
            start = date(2024, 1 + idx % 12, 1) if idx else date(2023, 6, 1)
            cid = o.create("hr.contract", {
                "name": f"Contrato {jname} - {name}",
                "employee_id": eid, "job_id": job_ids[job], "department_id": dept_ids[dept],
                "wage": float(wage), "date_start": start.isoformat(), "state": "open",
            })
            o.write("hr.contract", cid, {"state": "open"})
    log(f"RR. HH.: {o.count('hr.department', [])} departamentos, {o.count('hr.job', [])} cargos, "
        f"{o.count('hr.employee', [])} empleados, {o.count('hr.contract', [])} contratos.")
    return emp_ids


# ============================================================================ 5. PROVEEDORES
def setup_vendors(o):
    tag_id, _ = o.get_or_create("res.partner.category", [("name", "=", "Proveedor")], {"name": "Proveedor"})
    tag_out, _ = o.get_or_create("res.partner.category", [("name", "=", "Outsourcing")], {"name": "Outsourcing"})
    vendors = {}
    for name, vat, ctry, city, street, phone, email, cats in D.VENDORS:
        pid, _ = o.get_or_create("res.partner", [("name", "=", name)], {
            "name": name, "is_company": True, "vat": vat, "country_id": country_id(o, ctry), "city": city,
            "street": street, "phone": phone, "email": email, "supplier_rank": 1,
            "category_id": [(6, 0, [tag_id])], "lang": "es_419"})
        vendors[name] = {"id": pid, "cats": cats}
    outsourcing = {}
    for name, vat, ctry, city, street, phone, email, code, svc, price in D.OUTSOURCING_VENDORS:
        pid, _ = o.get_or_create("res.partner", [("name", "=", name)], {
            "name": name, "is_company": True, "vat": vat, "country_id": country_id(o, ctry), "city": city,
            "street": street, "phone": phone, "email": email, "supplier_rank": 1,
            "category_id": [(6, 0, [tag_id, tag_out])], "lang": "es_419"})
        outsourcing[name] = {"id": pid, "code": code, "service": svc, "price": price}
    log(f"Proveedores: {len(vendors)} de materiales + {len(outsourcing)} de outsourcing.")
    return vendors, outsourcing


# ============================================================================ 6. MATERIALES
def setup_materials(o, vendors, outsourcing, company_id):
    comp = o.search_read("res.company", [("id", "=", company_id)], ["account_purchase_tax_id"])[0]
    purchase_tax = comp["account_purchase_tax_id"][0] if comp.get("account_purchase_tax_id") else False
    if not purchase_tax:
        log("ADVERTENCIA: la empresa no tiene impuesto de compra por defecto.")
    unit = o.ref("uom.product_uom_unit")
    root, _ = o.get_or_create("product.category", [("name", "=", D.MATERIAL_ROOT), ("parent_id", "=", False)],
                              {"name": D.MATERIAL_ROOT})
    cat_ids = {}
    for code, name in D.MATERIAL_CATEGORIES.items():
        cat_ids[code], _ = o.get_or_create("product.category", [("name", "=", name), ("parent_id", "=", root)],
                                           {"name": name, "parent_id": root})
    vendors_by_cat = {}
    for vname, v in vendors.items():
        for c in v["cats"]:
            vendors_by_cat.setdefault(c, []).append(v["id"])

    materials = {}  # product.product id -> dict
    counters = {}
    for cat, name, cost in D.MATERIALS:
        counters[cat] = counters.get(cat, 0) + 1
        code = f"MAT-{cat}-{counters[cat]:02d}"
        found = o.search("product.template", [("default_code", "=", code)], limit=1)
        if found:
            tmpl = found[0]
        else:
            vals = {
                "name": name, "default_code": code, "categ_id": cat_ids[cat],
                "type": "consu", "is_storable": True,
                "sale_ok": False, "purchase_ok": True,
                "standard_price": cost, "list_price": round(cost * 1.35, 2),
                "uom_id": unit, "uom_po_id": unit,
                "purchase_method": "receive",
                "description_purchase": "Material de uso interno para la operación de las sucursales.",
                "seller_ids": [(0, 0, {"partner_id": pid, "price": round(cost * rng.uniform(0.93, 1.05), 2),
                                        "min_qty": 1, "delay": rng.randint(2, 10)})
                               for pid in vendors_by_cat[cat]],
            }
            if purchase_tax:
                vals["supplier_taxes_id"] = [(6, 0, [purchase_tax])]
            tmpl = o.create("product.template", vals)
        pid = o.search("product.product", [("product_tmpl_id", "=", tmpl)], limit=1)[0]
        materials[pid] = {"cat": cat, "cost": cost, "code": code}

    # Servicios de outsourcing (no cuentan como materiales)
    srv_cat, _ = o.get_or_create("product.category", [("name", "=", "Servicios de Outsourcing")], {"name": "Servicios de Outsourcing"})
    services = {}
    for vname, v in outsourcing.items():
        found = o.search("product.template", [("default_code", "=", v["code"])], limit=1)
        if found:
            tmpl = found[0]
        else:
            vals = {"name": v["service"], "default_code": v["code"], "categ_id": srv_cat, "type": "service",
                    "sale_ok": False, "purchase_ok": True, "standard_price": v["price"], "list_price": v["price"],
                    "purchase_method": "purchase",
                    "seller_ids": [(0, 0, {"partner_id": v["id"], "price": v["price"], "min_qty": 1})]}
            if purchase_tax:
                vals["supplier_taxes_id"] = [(6, 0, [purchase_tax])]
            tmpl = o.create("product.template", vals)
        pid = o.search("product.product", [("product_tmpl_id", "=", tmpl)], limit=1)[0]
        services[vname] = {"product_id": pid, "vendor_id": v["id"], "price": v["price"], "code": v["code"]}
    log(f"Materiales: {len(materials)} | Servicios de outsourcing: {len(services)} | Impuesto compra id={purchase_tax}")
    return materials, services, vendors_by_cat, purchase_tax


# ============================================================================ 7. COMPRAS
def receive_po(o, po_id, when):
    pickings = o.search_read("stock.picking", [("purchase_id", "=", po_id), ("state", "not in", ("done", "cancel"))], ["id"])
    for p in pickings:
        pid = p["id"]
        if o.search_read("stock.picking", [("id", "=", pid)], ["state"])[0]["state"] == "draft":
            o.call("stock.picking", "action_confirm", [pid])
        moves = o.search_read("stock.move", [("picking_id", "=", pid)], ["product_uom_qty"])
        for m in moves:
            o.write("stock.move", m["id"], {"quantity": m["product_uom_qty"], "picked": True})
        res = o.call("stock.picking", "button_validate", [pid])
        if isinstance(res, dict) and res.get("res_model"):
            # Por si Odoo pide confirmación (backorder / transferencia inmediata)
            wiz_model = res["res_model"]
            ctx = res.get("context", {})
            wiz = o.call(wiz_model, "create", {}, context=ctx)
            for meth in ("process", "process_cancel_backorder"):
                try:
                    o.call(wiz_model, meth, [wiz], context=ctx)
                    break
                except Exception:
                    continue
        o.write("stock.picking", pid, {"date_done": when})


def bill_po(o, po_id, inv_date, vendor_ref):
    po = o.search_read("purchase.order", [("id", "=", po_id)], ["invoice_ids", "invoice_status"])[0]
    if not po["invoice_ids"] and po["invoice_status"] == "to invoice":
        o.call("purchase.order", "action_create_invoice", [po_id])
        po = o.search_read("purchase.order", [("id", "=", po_id)], ["invoice_ids"])[0]
    bills = []
    for inv in o.search_read("account.move", [("id", "in", po["invoice_ids"])], ["state", "ref"]):
        if inv["state"] == "draft":
            o.write("account.move", inv["id"], {"invoice_date": inv_date.isoformat(), "date": inv_date.isoformat(),
                                                "ref": inv["ref"] or vendor_ref, "payment_reference": vendor_ref})
            o.call("account.move", "action_post", [inv["id"]])
        bills.append(inv["id"])
    return bills


def pay_bill(o, bill_id, pay_date):
    mv = o.search_read("account.move", [("id", "=", bill_id)], ["payment_state", "state"])[0]
    if mv["state"] != "posted" or mv["payment_state"] in ("paid", "in_payment"):
        return
    ctx = {"active_model": "account.move", "active_ids": [bill_id]}
    wiz = o.call("account.payment.register", "create", {"payment_date": pay_date.isoformat()}, context=ctx)
    o.call("account.payment.register", "action_create_payments", [wiz], context=ctx)


def setup_purchases(o, branches, materials, services, vendors_by_cat, purchase_tax):
    by_cat = {}
    for pid, m in materials.items():
        by_cat.setdefault(m["cat"], []).append(pid)
    branch_keys = list(branches.keys())
    weights = [0.5, 0.25, 0.25]
    today = date.today()

    existing = o.search_read("purchase.order", [("origin", "=", SEED_ORIGIN)], ["id"], order="id")
    n_existing = len(existing)
    log(f"Compras existentes del seed: {n_existing} / meta {D.TARGET_PURCHASES}")

    # Plan determinista (generador propio): siempre el mismo plan, se crean sólo las que faltan
    pr = random.Random(D.RANDOM_SEED + 1)
    plan = []
    svc_list = list(services.values())
    svc_every = max(1, D.TARGET_PURCHASES // D.TARGET_SERVICE_PURCHASES)
    for i in range(D.TARGET_PURCHASES):
        d_order = rand_date(r=pr)
        branch = pr.choices(branch_keys, weights)[0]
        n_svc = sum(1 for p in plan if p["kind"] == "svc")
        if i % svc_every == 3 and n_svc < D.TARGET_SERVICE_PURCHASES:
            s = svc_list[n_svc % len(svc_list)]
            qty = pr.randint(2, 6) if s["code"] == "SRV-TRA" else 1
            plan.append({"kind": "svc", "vendor": s["vendor_id"], "lines": [(s["product_id"], qty, s["price"])],
                         "date": d_order, "branch": branch, "hour": pr.randint(14, 22)})
            continue
        cat = pr.choice(sorted(D.MATERIAL_CATEGORIES.keys()))
        vendor = pr.choice(vendors_by_cat[cat])
        prods = pr.sample(sorted(by_cat[cat]), k=pr.randint(1, min(5, len(by_cat[cat]))))
        lines = []
        for p in prods:
            cost = materials[p]["cost"]
            qty = pr.randint(1, 6) if cost >= 1000 else pr.randint(4, 30) if cost >= 100 else pr.randint(10, 120)
            lines.append((p, qty, round(cost * pr.uniform(0.95, 1.06), 2)))
        plan.append({"kind": "mat", "vendor": vendor, "lines": lines, "date": d_order, "branch": branch,
                     "hour": pr.randint(14, 22)})
    plan.sort(key=lambda p: p["date"])

    po_ids = [p["id"] for p in existing]
    for i, p in enumerate(plan[n_existing:], start=n_existing + 1):
        vals = {
            "partner_id": p["vendor"], "origin": SEED_ORIGIN,
            "date_order": dt(p["date"], p["hour"]), "date_planned": dt(p["date"] + timedelta(days=3), 15),
            "picking_type_id": branches[p["branch"]]["in_type_id"],
            "notes": f"<p>Compra para {branches[p['branch']]['name']}.</p>",
            "order_line": [(0, 0, {"product_id": pid, "product_qty": q, "price_unit": pu,
                                   **({"taxes_id": [(6, 0, [purchase_tax])]} if purchase_tax else {})})
                           for pid, q, pu in p["lines"]],
        }
        po_ids.append(o.create("purchase.order", vals))
        if i % 10 == 0:
            log(f"  creadas {i}/{D.TARGET_PURCHASES} órdenes de compra")

    # Procesar todas (idempotente): confirmar -> recibir -> facturar -> pagar
    pos = o.search_read("purchase.order", [("id", "in", po_ids)], ["name", "state", "date_order", "partner_id"], order="date_order")
    for n, po in enumerate(pos, start=1):
        r = random.Random(f"{D.RANDOM_SEED}-{po['name']}")   # mismo resultado en cada corrida
        d_order = datetime.strptime(po["date_order"], "%Y-%m-%d %H:%M:%S").date()
        if po["state"] in ("draft", "sent", "to approve"):
            o.call("purchase.order", "button_confirm", [po["id"]])
            if po["state"] == "to approve":
                o.call("purchase.order", "button_approve", [po["id"]])
            o.write("purchase.order", po["id"], {"date_approve": dt(d_order, 16, r), "date_order": po["date_order"]})
        receive_po(o, po["id"], dt(min(d_order + timedelta(days=r.randint(1, 4)), today), 17, r))
        inv_date = min(d_order + timedelta(days=r.randint(2, 8)), today)
        ref = f"FACT-{po['partner_id'][0]:03d}-{po['name'].replace('/', '')}-{r.randint(1000, 9999)}"
        bills = bill_po(o, po["id"], inv_date, ref)
        pay_date = min(inv_date + timedelta(days=r.randint(3, 20)), today)
        if bills and r.random() < D.PAY_RATIO:
            for b in bills:
                pay_bill(o, b, pay_date)
        if n % 10 == 0:
            log(f"  procesadas {n}/{len(pos)} compras (confirmada + recibida + facturada)")

    # Solicitudes de cotización (RFQ) a proveedores
    n_rfq = o.count("purchase.order", [("origin", "=", SEED_RFQ_ORIGIN)])
    for _ in range(n_rfq, D.TARGET_RFQS):
        cat = rng.choice(list(D.MATERIAL_CATEGORIES.keys()))
        vendor = rng.choice(vendors_by_cat[cat])
        prods = rng.sample(by_cat[cat], k=rng.randint(2, 4))
        d = rand_date("2026-09-15", D.DATE_TO)
        o.create("purchase.order", {
            "partner_id": vendor, "origin": SEED_RFQ_ORIGIN, "date_order": dt(d),
            "picking_type_id": branches[rng.choice(branch_keys)]["in_type_id"],
            "order_line": [(0, 0, {"product_id": pid, "product_qty": rng.randint(5, 60),
                                   "price_unit": materials[pid]["cost"]}) for pid in prods]})
    log("Compras listas.")


# ============================================================================ RESUMEN
def summary(o):
    rows = [
        ("Empleados (>=35)", o.count("hr.employee", []), 35),
        ("Cargos (>=6)", o.count("hr.job", []), 6),
        ("Departamentos (>=5)", o.count("hr.department", []), 5),
        ("Compras confirmadas (>=100)", o.count("purchase.order", [("state", "in", ("purchase", "done"))]), 100),
        ("Compras facturadas", o.count("purchase.order", [("state", "in", ("purchase", "done")), ("invoice_status", "=", "invoiced")]), 100),
        ("Facturas de proveedor publicadas", o.count("account.move", [("move_type", "=", "in_invoice"), ("state", "=", "posted")]), 100),
        ("Facturas totales publicadas (>=50)", o.count("account.move", [("move_type", "in", ("in_invoice", "out_invoice")), ("state", "=", "posted")]), 50),
        ("Materiales (>=60)", o.count("product.template", [("default_code", "=like", "MAT-%")]), 60),
        ("Cotizaciones a proveedores (RFQ)", o.count("purchase.order", [("state", "in", ("draft", "sent"))]), 0),
    ]
    log("=" * 64)
    ok_all = True
    for label, val, target in rows:
        ok = val >= target
        ok_all &= ok
        log(f"  {'OK ' if ok else 'FALTA'} {label:<40} {val}")
    log("=" * 64)
    return ok_all


def main():
    ensure_database()
    o = Odoo(URL, DB, LOGIN, PASSWORD).connect()
    install_modules(o)
    company_id, company_partner = setup_company(o)
    enable_settings(o)
    branches = setup_branches(o, company_partner)
    setup_hr(o, branches)
    vendors, outsourcing = setup_vendors(o)
    materials, services, vendors_by_cat, purchase_tax = setup_materials(o, vendors, outsourcing, company_id)
    setup_purchases(o, branches, materials, services, vendors_by_cat, purchase_tax)
    ok = summary(o)
    if os.environ.get("SEED_SKIP_PDF") != "1":
        import export_invoices
        export_invoices.export_all(o, PDF_OUT)
    log("Listo. " + ("Todas las metas de la rúbrica (Integrante 3) se cumplen." if ok else "Revisa las metas marcadas como FALTA."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
