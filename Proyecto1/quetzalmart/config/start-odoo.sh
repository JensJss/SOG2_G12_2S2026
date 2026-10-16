#!/bin/bash
# -----------------------------------------------------------------------------
# Arranque de Odoo para QuetzalMart.
# Genera /tmp/odoo.conf a partir de variables de entorno (.env) para no
# guardar contraseñas en archivos versionados, y luego ejecuta Odoo.
# -----------------------------------------------------------------------------
set -euo pipefail

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"
: "${DB_USER:=odoo}"
: "${DB_PASSWORD:?DB_PASSWORD vacío}"
: "${ODOO_DB:=quetzalmart}"
: "${ODOO_MASTER_PASSWORD:?ODOO_MASTER_PASSWORD vacío}"
: "${ODOO_LIST_DB:=True}"
: "${ODOO_PROXY_MODE:=False}"

CONF=/tmp/odoo.conf

cat > "$CONF" <<EOF
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
admin_passwd = ${ODOO_MASTER_PASSWORD}
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}
db_maxconn = 32
dbfilter = ^${ODOO_DB}\$
list_db = ${ODOO_LIST_DB}
proxy_mode = ${ODOO_PROXY_MODE}
http_port = 8069
; Modo multihilo: HTTP + websocket en el mismo puerto 8069 (ideal para t3.small)
workers = 0
max_cron_threads = 1
without_demo = all
log_level = info
EOF

# Si la base ya existe, la precargamos para que los crons (cola de correos,
# campañas de marketing, etc.) corran desde el arranque sin esperar una visita.
if python3 - <<PY
import sys, psycopg2
try:
    c = psycopg2.connect(host="${DB_HOST}", port=${DB_PORT}, user="${DB_USER}",
                         password="""${DB_PASSWORD}""", dbname="postgres", connect_timeout=5)
    cur = c.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", ("${ODOO_DB}",))
    found = cur.fetchone() is not None
    if found:
        c2 = psycopg2.connect(host="${DB_HOST}", port=${DB_PORT}, user="${DB_USER}",
                              password="""${DB_PASSWORD}""", dbname="${ODOO_DB}", connect_timeout=5)
        cur2 = c2.cursor()
        cur2.execute("SELECT to_regclass('public.ir_module_module') IS NOT NULL")
        found = cur2.fetchone()[0]
    sys.exit(0 if found else 1)
except Exception as e:
    print("check db:", e, file=sys.stderr)
    sys.exit(1)
PY
then
    echo "db_name = ${ODOO_DB}" >> "$CONF"
    echo "[quetzalmart] Base '${ODOO_DB}' encontrada: se precarga."
else
    echo "[quetzalmart] Base '${ODOO_DB}' aún no existe: créala con 'docker compose --profile seed run --rm seed'."
fi

exec odoo -c "$CONF" "$@"
