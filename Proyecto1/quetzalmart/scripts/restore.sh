#!/bin/bash
# Restaura un respaldo creado con scripts/backup.sh (REEMPLAZA la base actual, pide confirmación).
# Uso:  bash scripts/restore.sh backups/quetzalmart_YYYYmmdd_HHMM      (sin extensión)
set -euo pipefail
cd "$(dirname "$0")/.."
PREFIX="${1:?Uso: bash scripts/restore.sh backups/<db>_<fecha>   (sin extensión)}"
PREFIX="${PREFIX%.dump}"; PREFIX="${PREFIX%.filestore.tgz}"
[ -f "${PREFIX}.dump" ] || { echo "No existe ${PREFIX}.dump"; exit 1; }
set -a; source .env; set +a
DB="${ODOO_DB:-quetzalmart}"
PGU="${POSTGRES_USER:-odoo}"

read -r -p "Se REEMPLAZARÁ la base '$DB' y su filestore. Escribe SI para continuar: " ok
[ "$ok" = "SI" ] || { echo "Cancelado."; exit 1; }

docker compose up -d db
docker compose stop odoo
docker compose exec -T db dropdb -U "$PGU" --if-exists "$DB"
docker compose exec -T db createdb -U "$PGU" "$DB"
docker compose exec -T db pg_restore -U "$PGU" -d "$DB" --no-owner --role="$PGU" < "${PREFIX}.dump"

if [ -f "${PREFIX}.filestore.tgz" ]; then
  docker compose run --rm --no-deps -T --entrypoint bash odoo -c \
    "mkdir -p /var/lib/odoo/filestore && rm -rf '/var/lib/odoo/filestore/$DB' && tar xzf - -C /var/lib/odoo/filestore" \
    < "${PREFIX}.filestore.tgz"
fi

docker compose up -d odoo
echo "Base '$DB' restaurada."
echo "Si la URL pública cambió:  docker compose --profile seed run --rm -e SEED_SKIP_PDF=1 seed"
