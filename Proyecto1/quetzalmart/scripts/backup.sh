#!/bin/bash
# Respaldo completo de QuetzalMart: base de datos (pg_dump) + filestore (adjuntos/imágenes).
# Funciona aunque ODOO_LIST_DB=False.   Uso (EC2 / Linux / Git Bash):  bash scripts/backup.sh
# Genera:  backups/<db>_<fecha>.dump  y  backups/<db>_<fecha>.filestore.tgz
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a
DB="${ODOO_DB:-quetzalmart}"
PGU="${POSTGRES_USER:-odoo}"
STAMP="$(date +%Y%m%d_%H%M)"
mkdir -p backups
PREFIX="backups/${DB}_${STAMP}"

docker compose exec -T db pg_dump -U "$PGU" -Fc --no-owner "$DB" > "${PREFIX}.dump"
docker compose exec -T odoo bash -c "cd /var/lib/odoo/filestore 2>/dev/null && tar czf - '$DB' || tar czf - --files-from /dev/null" > "${PREFIX}.filestore.tgz"

echo "Respaldo listo:"
ls -lh "${PREFIX}".*
echo "Restaurar con:  bash scripts/restore.sh ${PREFIX}"
