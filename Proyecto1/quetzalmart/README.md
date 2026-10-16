# QuetzalMart · ERP Odoo 18 Community

Proyecto único de **Sistemas Organizacionales y Gerenciales 2** (USAC, 2.º semestre 2026).
El ERP (Odoo 18 Community) y su base de datos (PostgreSQL 16) corren **en la misma VM** con Docker Compose.
El mismo proyecto funciona igual en la PC local y en una **EC2 de AWS**.

| Pieza | Imagen | Puerto local (PC) | Puerto en EC2 |
|---|---|---|---|
| Odoo 18 (ERP + sitio web + eCommerce + CRM) | `odoo:18.0` | **18069** | 80 (nginx) |
| PostgreSQL 16 | `postgres:16` | **127.0.0.1:15432** | 127.0.0.1:5432 (túnel SSH) |
| nginx (perfil `proxy`) | `nginx:1.27-alpine` | — | **80** |
| Mailpit (perfil `dev`, solo pruebas) | `axllent/mailpit` | 127.0.0.1:18025 | — |
| Adminer (perfil `tools`, cliente SQL web) | `adminer:4` | 127.0.0.1:18081 | 127.0.0.1:18081 (túnel SSH) |

> **Puertos de la PC del Integrante 3:** 8069, 8072, 8080, 5432, 1025, 8025, 27017, 1433, 8070, 8090 y demás
> ya están ocupados por otros proyectos (`rutamoto-*`, `postgres_db`, `temis-dashboard`, `mongodb_local`…).
> Por eso aquí se usan 18069 / 15432 / 18025 / 18081. Los contenedores, la red (`quetzalmart-net`) y los
> volúmenes (`quetzalmart_*`) tienen nombres propios: **no tocan nada de los otros proyectos**.

---

## 1. Arranque rápido (PC local)

Requisitos: Docker Desktop. **No se necesita Docker Hub** si ya tienes las imágenes `odoo:18.0` y `postgres:16`
(Compose solo descarga lo que falta).

```powershell
cd quetzalmart
copy .env.example .env            # (Linux/Mac: cp .env.example .env)
docker compose up -d              # levanta db + odoo
docker compose --profile seed run --rm seed   # crea la base y carga TODO (≈ 8-12 min la 1.ª vez)
```

Abrir **http://localhost:18069** → usuario `admin`, contraseña la de `ODOO_ADMIN_PASSWORD` en `.env`.

> Si Docker responde *"ports are not available"*, puede ser que Windows (Hyper-V/WSL) tenga reservado un
> rango de puertos. Para revisarlo: `netsh interface ipv4 show excludedportrange protocol=tcp`. Si 18069 o
> 15432 aparecen ahí, cambia `ODOO_PORT`/`PG_PORT` en `.env` (por ejemplo 18169 / 15433), luego
> `docker compose up -d` y ajusta `ODOO_PUBLIC_URL`.

## 2. Despliegue en AWS EC2

Guía paso a paso, incluida la apertura de puertos del Security Group: **[docs/EC2_DESPLIEGUE.md](docs/EC2_DESPLIEGUE.md)**

Resumen:
```bash
# en la EC2 (Ubuntu 24.04)
curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker $USER && newgrp docker
# subir esta carpeta (git clone o scp), luego:
cd quetzalmart && cp .env.ec2.example .env && nano .env      # cambiar contraseñas e IP
docker compose --profile proxy up -d
docker compose --profile seed run --rm seed
```

## 3. ¿Qué carga el seed? (Integrante 3 · ERP administrativo)

| Rúbrica | Requisito | Cargado |
|---|---|---|
| 1.03 Empleados | ≥ 35 | **37** (36 de la cadena + el admin), con correo, teléfono, sucursal, jefe y **contrato** |
| 1.04 Cargos | ≥ 6 | **8** |
| 1.05 Departamentos | ≥ 5 | **5** |
| 1.06 Compras + facturas | ≥ 100 | **105** órdenes confirmadas → recibidas en bodega → facturadas (IVA 12 %) → ~80 % pagadas |
| 1.07 Materiales | ≥ 60 | **64** en 8 categorías, con proveedor y existencias por sucursal |
| 1.08 Facturas | ≥ 50 PDF | **105** PDF en `facturas_pdf/compras/` + `indice_facturas.csv` |
| 1.02 (apoyo) | cotizaciones | **12** solicitudes de cotización a proveedores (el Integrante 4 agrega las de clientes) |
| Base equipo | — | Empresa, logo, 3 sucursales (GT/MX/SV), GTQ, IVA 12 % (l10n_gt), módulos de todos instalados |

El seed es **idempotente**: si se corre otra vez, solo completa lo que falte (no duplica).

Módulos instalados para todo el equipo: Contactos, Empleados, Contratos, Compras, Inventario, Facturación
(+ localización Guatemala), Ventas, CRM, Sitio web, eCommerce, Email Marketing, Reglas automatizadas y
**Gestión documental OCA `dms`** (incluida en `addons/`).

## 4. Consultas SQL de la calificación

```bash
docker compose exec db psql -U odoo -d quetzalmart -f /sql/consultas_calificacion.sql
```
Trae un **resumen con todas las metas** de la rúbrica y luego el detalle por criterio (empleados, cargos,
departamentos, compras + facturas, materiales, facturas, ventas, cotizaciones, clientes/productos del RPA,
gestor documental y marketing). Detalle en [docs/INTEGRANTE3_ERP.md](docs/INTEGRANTE3_ERP.md).

## 5. Comandos útiles

| Acción | Comando |
|---|---|
| Ver estado | `docker compose ps` |
| Ver logs de Odoo | `docker compose logs -f odoo` |
| Re-exportar PDFs (p. ej. facturas creadas en la calificación) | `docker compose --profile seed run --rm --entrypoint python3 seed -u /seed/export_invoices.py` |
| Consola SQL | `docker compose exec db psql -U odoo -d quetzalmart` |
| Cliente SQL web (Adminer) | `docker compose --profile tools up -d adminer` → http://localhost:18081 (servidor `db`, usuario `odoo`) |
| Respaldo (BD + adjuntos) | `bash scripts/backup.sh` (EC2/Linux o Git Bash) |
| Restaurar | `bash scripts/restore.sh backups/quetzalmart_AAAAMMDD_HHMM` |
| Detener (conserva datos) | `docker compose down` |
| ⚠️ Borrar TODO (datos incluidos) | `docker compose down -v` — solo dentro de esta carpeta |

## 6. Estructura

```
quetzalmart/
├─ docker-compose.yml        # db + odoo (+ perfiles seed / proxy / dev / tools)
├─ .env.example              # variables para la PC local (puertos libres)
├─ .env.ec2.example          # variables para la EC2
├─ config/start-odoo.sh      # genera odoo.conf desde .env y arranca Odoo
├─ nginx/odoo.conf           # proxy inverso (puerto 80, websocket)
├─ addons/                   # módulos extra: OCA dms, dms_field, hr_dms_field (LGPL-3)
├─ seed/                     # carga de datos Integrante 3 (XML-RPC, solo librería estándar)
│  ├─ seed.py  data.py  export_invoices.py  qm_rpc.py
├─ sql/consultas_calificacion.sql   # todas las consultas de la rúbrica + resumen de metas
├─ carga_masiva/             # plantillas Excel para 'Importar registros' (datos_* y demo_*)
├─ scripts/                  # ec2-bootstrap.sh, backup.sh, restore.sh, generar_carga_masiva.py
├─ facturas_pdf/             # salida de PDFs (se genera)
└─ docs/                     # EC2, Integrante 3, traspaso al equipo, prompt para el siguiente agente
```

## 7. Para los demás integrantes
Ver **[docs/TRASPASO_EQUIPO.md](docs/TRASPASO_EQUIPO.md)** y **[docs/PROMPT_SIGUIENTE_AGENTE.md](docs/PROMPT_SIGUIENTE_AGENTE.md)**.
