# Plan de riesgos · QuetzalMart en EC2

Todo se ejecuta en la EC2 dentro de `~/quetzalmart`. Conexión: `ssh -i GERENCIALES2.pem ec2-user@IP`.

**Una sola vez (recomendado):** `bash scripts/recuperar.sh --instalar`
Con eso la VM se recupera sola en cada arranque y saca un respaldo diario a las 03:00 (guarda 3 días).

| # | Riesgo | Cómo se nota | Qué hacer |
|---|---|---|---|
| 1 | **Reinicio de la instancia** (Reboot) | El sitio no responde unos minutos | La IP **no cambia**. Docker y los contenedores arrancan solos. Si a los 3 min no responde: `bash scripts/recuperar.sh` |
| 2 | **Detener → Iniciar** (Stop/Start) | La IP pública **cambia** y el link viejo no abre | En la consola de EC2 ver la nueva *Public IPv4*, entrar por SSH con la IP nueva y correr `bash scripts/recuperar.sh` (con `--instalar` ya hecho lo hace solo). Avisar la IP nueva al equipo. Para evitarlo: asignar una **Elastic IP** |
| 3 | **Odoo caído o lento** (falta de RAM, error) | 502 Bad Gateway o carga infinita | `docker compose logs --tail 80 odoo`, luego `docker compose --profile proxy restart odoo`. Si persiste: `bash scripts/recuperar.sh` |
| 4 | **Borrado accidental de datos** | Faltan registros / metas en 0 | Restaurar el último respaldo: `ls backups/` → `bash scripts/restore.sh backups/quetzalmart_AAAAMMDD_HHMM`. Si no hay respaldo, el seed reconstruye la parte del Integrante 3: `docker compose --profile seed run --rm seed` (con `ODOO_LIST_DB=True` si la base fue eliminada) |
| 5 | **Alguien corrió `docker compose down -v`** | Base vacía | Igual que el riesgo 4: restaurar el respaldo. Lo del Integrante 3 se regenera con el seed, pero lo que los demás cargaron a mano solo vuelve con un respaldo |
| 6 | **Disco lleno** | Errores al guardar o subir archivos | `df -h /` y `docker system df`. Limpiar con `docker image prune -f` y respaldos viejos en `backups/`. Se puede ampliar el volumen EBS desde la consola |
| 7 | **Se pierde la llave `.pem`** | No se puede entrar por SSH | Consola EC2 → la instancia → **Connect → EC2 Instance Connect** (desde el navegador, usuario `ec2-user`) |
| 8 | **No llegan los correos** | El auxiliar no recibe la compra o la campaña | AWS bloquea el puerto 25: usar SMTP 587/465. Revisar *Ajustes → Técnico → Correos* (cola) y bajar la acción planificada *Mail: Email Queue Manager* a 1 minuto |
| 9 | **PDFs sin estilos** | Facturas sin logo ni formato | El parámetro `report.url` debe ser `http://localhost:8069` (*Ajustes → Técnico → Parámetros del sistema*) |
| 10 | **Cuenta AWS sin crédito / instancia terminada** | La instancia desaparece | Crear una EC2 nueva (`docs/EC2_DESPLIEGUE.md`), restaurar el último respaldo bajado a la PC o correr el seed. Por eso conviene **bajar un respaldo** a la PC antes de la calificación: `scp -r -i GERENCIALES2.pem ec2-user@IP:~/quetzalmart/backups .` |

**Antes de la calificación (checklist de 2 minutos):**
```bash
cd ~/quetzalmart
bash scripts/recuperar.sh          # verifica todo y muestra el resumen de metas
bash scripts/backup.sh             # respaldo fresco
```
