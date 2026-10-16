# Despliegue en AWS EC2 (Odoo 18 + PostgreSQL 16 en la misma VM)

Requisito del enunciado: *"ERP implementado en la nube"* y *"base de datos también implementada en la nube"*.
Ambas cosas quedan en la misma EC2: Postgres corre en un contenedor junto a Odoo.

---

## 1. Crear la instancia

En **EC2 → Instances → Launch instances**:

| Campo | Valor recomendado |
|---|---|
| Name | `quetzalmart-erp` |
| AMI | **Amazon Linux 2023** (usuario `ec2-user`) o **Ubuntu 24.04** (usuario `ubuntu`), x86_64 |
| Instance type | **t3.small** (2 vCPU, 2 GiB), que es el mínimo cómodo. **t3.medium** (4 GiB) si les alcanza. Con t3.micro (1 GiB) Odoo se queda sin memoria al instalar los módulos, aunque haya swap. |
| Key pair | Crear `quetzalmart-key` (.pem) y **compartirla solo con el equipo** |
| Network settings | Crear un Security Group nuevo `quetzalmart-sg` (reglas en el paso 2) |
| Storage | **25 GiB gp3** |

Después, en **Elastic IPs → Allocate → Associate** con la instancia. Así la IP no cambia si la detienen;
de lo contrario hay que actualizar `ODOO_PUBLIC_URL` cada vez.

> Revisen cuánto cuesta el tipo de instancia en su cuenta (free tier o créditos). Detener la instancia
> cuando no se use ahorra dinero y conserva los datos (disco EBS).

---

## 2. Abrir los puertos (Security Group)

**EC2 → Security Groups → `quetzalmart-sg` → Inbound rules → Edit inbound rules → Add rule**

| # | Tipo | Protocolo | Puerto | Origen (Source) | Para qué | ¿Abrir? |
|---|---|---|---|---|---|---|
| 1 | SSH | TCP | **22** | **My IP** (y la IP `/32` de cada integrante) | Administrar la VM, correr el seed, consultas SQL | ✅ Sí |
| 2 | HTTP | TCP | **80** | `0.0.0.0/0` y `::/0` | Sitio web, eCommerce y ERP (nginx → Odoo). Es lo que usa el auxiliar | ✅ Sí |
| 3 | HTTPS | TCP | **443** | `0.0.0.0/0` y `::/0` | Solo si configuran dominio + certificado TLS | ⚪ Opcional |
| 4 | PostgreSQL | TCP | **5432** | **Solo IPs `/32` del equipo** (nunca `0.0.0.0/0`) | DBeaver/pgAdmin directo, sin túnel. Requiere `PG_BIND=0.0.0.0` en `.env` | ⚪ Opcional (se recomienda túnel SSH) |
| 5 | Custom TCP | TCP | **8069** | My IP | Entrar a Odoo sin nginx (diagnóstico). Requiere `ODOO_BIND=0.0.0.0` | ⚪ Opcional |

**No abrir:** 18081 (Adminer) ni 8025 (Mailpit). Se usan por túnel SSH.
**Outbound rules:** dejar la regla por defecto (todo el tráfico). Odoo necesita salir a internet para
SMTP (587/465), Google Analytics y pasarelas de pago. AWS bloquea el puerto 25 de salida, así que usen 587.

Lo mismo con AWS CLI (reemplazar `sg-XXXX` y `TU.IP.PUB.LICA`):
```bash
SG=sg-XXXX
aws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 22  --cidr TU.IP.PUB.LICA/32
aws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 80  --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG --ip-permissions IpProtocol=tcp,FromPort=80,ToPort=80,Ipv6Ranges='[{CidrIpv6=::/0}]'
# opcional HTTPS
aws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 443 --cidr 0.0.0.0/0
# opcional Postgres SOLO para una IP del equipo
aws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 5432 --cidr IP.DEL.COMPANERO/32
```

> El firewall de Ubuntu (ufw) viene desactivado en las AMIs de AWS. Quien filtra es el Security Group.
> Si alguien activa ufw, Docker publica los puertos por encima de él igualmente.

---

## 3. Preparar la VM

```bash
ssh -i quetzalmart-key.pem ec2-user@IP_PUBLICA
```

Subir el proyecto con **una** de estas opciones:
```bash
# A) Git (recomendado: repo privado del equipo)
git clone https://github.com/USUARIO/quetzalmart.git && cd quetzalmart

# B) ZIP desde la PC (PowerShell o Git Bash en Windows)
scp -i quetzalmart-key.pem quetzalmart.zip ec2-user@IP_PUBLICA:~
#    y en la EC2:
sudo apt-get update && sudo apt-get install -y unzip && unzip quetzalmart.zip && cd quetzalmart
```

Instalar Docker, crear 2 GB de swap y fijar la zona horaria (una sola vez):
```bash
bash scripts/ec2-bootstrap.sh
newgrp docker          # o cerrar y abrir la sesión SSH
```

---

## 4. Configurar y levantar

```bash
cp .env.ec2.example .env
nano .env
```
Cambiar como mínimo: `POSTGRES_PASSWORD`, `ODOO_MASTER_PASSWORD`, `ODOO_ADMIN_PASSWORD` (solo letras,
números, `-` y `_`) y `ODOO_PUBLIC_URL=http://IP_ELASTICA`.

```bash
docker compose --profile proxy up -d             # db + odoo + nginx (puerto 80)
docker compose ps                                # esperar a que odoo esté "healthy"
docker compose --profile seed run --rm seed      # crea la BD y carga los datos (8-12 min)
```

Al terminar, el seed muestra el resumen `OK` de cada meta y genera `facturas_pdf/`.
Abrir **http://IP_ELASTICA** y entrar con `admin` y la contraseña de `ODOO_ADMIN_PASSWORD`.

**Cerrar el gestor de bases**, para que nadie pueda borrar o crear bases desde la web:
```bash
sed -i 's/^ODOO_LIST_DB=.*/ODOO_LIST_DB=False/' .env
docker compose --profile proxy up -d odoo        # recrea solo Odoo con la nueva config
```
Para volver a crear la base desde cero, ponerlo otra vez en `True`.

---

## 5. Durante la calificación

**Consultas SQL (la BD está en la nube, dentro de la EC2):**
```bash
ssh -i quetzalmart-key.pem ec2-user@IP_ELASTICA
cd quetzalmart
docker compose exec db psql -U odoo -d quetzalmart -f /sql/consultas_calificacion.sql   # todo
docker compose exec db psql -U odoo -d quetzalmart                                       # interactivo
```

**DBeaver / pgAdmin desde la PC por túnel SSH** (sin abrir el 5432):
- Pestaña *Main*: Host `localhost`, Port `5432`, Database `quetzalmart`, User `odoo`, Password = `POSTGRES_PASSWORD`
- Pestaña *SSH*: Use SSH tunnel, Host `IP_ELASTICA`, Port 22, User `ec2-user` (o `ubuntu`), Auth *Public key* → `quetzalmart-key.pem`

**Adminer por túnel:**
```bash
docker compose --profile tools up -d adminer               # en la EC2
ssh -i quetzalmart-key.pem -L 18081:localhost:18081 ec2-user@IP_ELASTICA   # en la PC
# abrir http://localhost:18081  ->  Sistema PostgreSQL, Servidor db, Usuario odoo, BD quetzalmart
```

**Carpeta con los PDF de facturas (rúbrica 1.08 / 1.09):**
```bash
# después de generar facturas nuevas en vivo:
docker compose --profile seed run --rm --entrypoint python3 seed -u /seed/export_invoices.py
ls facturas_pdf/compras | wc -l
# bajarla a la PC para mostrarla en el explorador de archivos:
scp -r -i quetzalmart-key.pem ec2-user@IP_ELASTICA:~/quetzalmart/facturas_pdf .
```

---

## 6. Si cambia la IP o el dominio

```bash
nano .env                                   # actualizar ODOO_PUBLIC_URL
docker compose --profile seed run --rm -e SEED_SKIP_PDF=1 seed   # re-aplica web.base.url (no duplica datos)
```

## 7. HTTPS (opcional)

Con un dominio apuntando a la IP elástica, lo más sencillo es certbot sobre la EC2 o reemplazar nginx
por Caddy. Recuerden abrir el 443 y poner `ODOO_PUBLIC_URL=https://dominio`.

## 8. Problemas comunes

| Síntoma | Causa / solución |
|---|---|
| `odoo` reinicia en bucle o se cae al instalar módulos | Falta RAM. Usen t3.small o mayor y confirmen el swap con `free -h` |
| 502 Bad Gateway en el puerto 80 | Odoo aún arranca. Revisen `docker compose logs -f odoo` |
| PDFs sin estilos o sin logo | `report.url` debe ser `http://localhost:8069`, que es lo que pone el seed. Revisen en Ajustes → Técnico → Parámetros del sistema |
| `permission denied` al escribir `facturas_pdf` | `sudo chown -R 1000:1000 facturas_pdf` (o ajustar `HOST_UID`/`HOST_GID` en `.env`) |
| No llegan correos | AWS bloquea el 25. Configuren SMTP con puerto 587 en Ajustes → Técnico → Servidores de correo saliente |
| `Database manager has been disabled` | Esperado con `ODOO_LIST_DB=False`. Solo hace falta en `True` para crear la base |
