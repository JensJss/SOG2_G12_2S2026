#!/bin/bash
# =============================================================================
#  QuetzalMart · Recuperación después de reiniciar / detener-iniciar la EC2
#
#  Uso manual (en la EC2):     bash ~/quetzalmart/scripts/recuperar.sh
#  Dejarlo automático:         bash ~/quetzalmart/scripts/recuperar.sh --instalar
#     -> corre solo en cada arranque de la VM + respaldo diario a las 03:00
#
#  Hace: arranca Docker y el swap, detecta la IP pública NUEVA (si cambió por
#  detener/iniciar), actualiza .env y web.base.url de Odoo, levanta db+odoo+nginx,
#  espera a que Odoo responda y muestra el resumen de metas de la rúbrica.
# =============================================================================
set -uo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"
log() { echo "[$(date '+%H:%M:%S')] $*"; }

# ---------------------------------------------------------------- instalación
if [ "${1:-}" = "--instalar" ]; then
  U="$(whoami)"
  sudo tee /etc/systemd/system/quetzalmart-recuperar.service >/dev/null <<EOF
[Unit]
Description=QuetzalMart - recuperar servicios al arrancar
After=docker.service network-online.target
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
User=$U
WorkingDirectory=$DIR
ExecStart=/bin/bash $DIR/scripts/recuperar.sh
RemainAfterExit=yes
TimeoutStartSec=900

[Install]
WantedBy=multi-user.target
EOF
  sudo tee /etc/systemd/system/quetzalmart-respaldo.service >/dev/null <<EOF
[Unit]
Description=QuetzalMart - respaldo diario (BD + filestore)
Requires=docker.service

[Service]
Type=oneshot
User=$U
WorkingDirectory=$DIR
ExecStart=/bin/bash $DIR/scripts/backup.sh
ExecStartPost=/usr/bin/find $DIR/backups -type f -mtime +3 -delete
EOF
  sudo tee /etc/systemd/system/quetzalmart-respaldo.timer >/dev/null <<EOF
[Unit]
Description=QuetzalMart - respaldo diario 03:00

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
  sudo systemctl daemon-reload
  sudo systemctl enable quetzalmart-recuperar.service
  sudo systemctl enable --now quetzalmart-respaldo.timer
  log "Instalado: recuperación automática al arrancar + respaldo diario 03:00 (se guardan 3 días en backups/)."
  log "Ver estado: systemctl status quetzalmart-recuperar  |  systemctl list-timers | grep quetzalmart"
  exit 0
fi

[ -f .env ] || { echo "No existe $DIR/.env (cópialo de .env.ec2.example y configúralo)."; exit 1; }
set -a; . ./.env; set +a
PGU="${POSTGRES_USER:-odoo}"; DB="${ODOO_DB:-quetzalmart}"; PORT="${ODOO_PORT:-8069}"

# ---------------------------------------------------------------- 1. Docker y swap
log "1/5 Docker y swap"
sudo systemctl start docker
if [ -f /swapfile ] && ! swapon --show | grep -q /swapfile; then sudo swapon /swapfile && log "    swap activado"; fi

# ---------------------------------------------------------------- 2. IP pública actual (IMDSv2)
log "2/5 Detectando IP pública"
TOKEN=$(curl -s -m 3 -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 120" || true)
IP=$(curl -s -m 3 -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 || true)
if [[ ! "$IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  log "    No se pudo leer la IP pública (se mantiene ${ODOO_PUBLIC_URL})"; IP=""
else
  log "    IP pública: $IP"
fi

# ---------------------------------------------------------------- 3. Base de datos
log "3/5 Levantando PostgreSQL"
docker compose up -d db >/dev/null
for i in $(seq 1 30); do
  docker compose exec -T db pg_isready -U "$PGU" -d postgres >/dev/null 2>&1 && break; sleep 2
done

NEW_URL=""
if [ -n "$IP" ] && [ "${ODOO_PUBLIC_URL:-}" != "http://$IP" ]; then
  NEW_URL="http://$IP"
  log "    La IP cambió: ${ODOO_PUBLIC_URL:-?} -> $NEW_URL (actualizando .env y Odoo)"
  sed -i "s|^ODOO_PUBLIC_URL=.*|ODOO_PUBLIC_URL=$NEW_URL|" .env
  docker compose exec -T db psql -U "$PGU" -d "$DB" -qc \
    "UPDATE ir_config_parameter SET value='$NEW_URL' WHERE key='web.base.url';" \
    || log "    ADVERTENCIA: no se pudo actualizar web.base.url"
fi

# ---------------------------------------------------------------- 4. Odoo + nginx
log "4/5 Levantando Odoo + nginx"
if [ -n "$NEW_URL" ]; then docker compose --profile proxy up -d --force-recreate odoo nginx >/dev/null
else docker compose --profile proxy up -d >/dev/null; fi
OK=0
for i in $(seq 1 60); do
  if curl -sf -m 5 "http://127.0.0.1:${PORT}/web/health" >/dev/null; then OK=1; break; fi
  sleep 5
done
[ $OK = 1 ] && log "    Odoo responde" || log "    ERROR: Odoo no responde. Revisa: docker compose logs --tail 80 odoo"
curl -s -o /dev/null -w "    nginx (puerto 80) -> HTTP %{http_code}\n" -m 10 http://127.0.0.1/web/login || true

# ---------------------------------------------------------------- 5. Resumen
log "5/5 Estado"
docker compose --profile proxy ps --format "table {{.Name}}\t{{.Status}}"
free -h | awk 'NR<=3'
df -h / | awk 'NR==1 || NR==2'
docker compose exec -T db psql -U "$PGU" -d "$DB" -f /sql/consultas_calificacion.sql 2>/dev/null | sed -n '3,17p'
echo
log "Sitio: ${NEW_URL:-${ODOO_PUBLIC_URL}}"
[ -n "$NEW_URL" ] && log "AVISA AL EQUIPO: la IP cambió a $IP (SSH: ssh -i GERENCIALES2.pem ec2-user@$IP)"
exit 0
