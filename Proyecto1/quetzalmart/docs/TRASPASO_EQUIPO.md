# Traspaso al equipo · QuetzalMart

## 0. Lo que ya está listo (Integrante 3)

- Infraestructura Docker lista para la EC2: Odoo 18 Community + PostgreSQL 16 en la misma VM y nginx en el puerto 80.
- Base `quetzalmart` en español (es_419), con la empresa QuetzalMart, S.A. (logo, NIT, GTQ, IVA 12 %),
  3 sucursales/almacenes (GT, MX, SV) y la localización contable de Guatemala.
- Módulos ya instalados para **todos**: Empleados, Contratos, Compras, Inventario, Facturación, Ventas, CRM,
  Sitio web, eCommerce, Email Marketing, Reglas automatizadas y Documentos (OCA `dms`).
- Datos de la rúbrica 1.03 a 1.08 cargados y verificados: 37 empleados, 8 cargos, 5 departamentos,
  105 compras con su factura, 64 materiales, 105 PDF de facturas y 12 cotizaciones a proveedores.
- Consultas SQL de **toda** la rúbrica en `sql/consultas_calificacion.sql`. Las secciones de cada integrante
  devuelven 0 filas hasta que carguen sus datos.

## 1. Cómo pasar el trabajo (la forma más sencilla)

**Regla de oro: la EC2 es la única fuente de verdad.** Todos trabajan sobre el mismo Odoo en la nube
(`http://IP_ELASTICA`), que además es el que se califica. Así nadie tiene que fusionar bases de datos.

1. Quien administre AWS crea la EC2 siguiendo `docs/EC2_DESPLIEGUE.md`, sube esta carpeta y corre el seed. Son unos 20 minutos.
2. Se comparte con el equipo, **por privado y nunca en el repo**:
   - URL `http://IP_ELASTICA`, usuario `admin` y la contraseña de `ODOO_ADMIN_PASSWORD`
   - `quetzalmart-key.pem` (SSH) y el `.env` de la EC2 (contraseñas de BD y maestra)
3. El código (este repo) va a un **GitHub privado**:
   ```bash
   git init && git add . && git commit -m "QuetzalMart: infraestructura + ERP Integrante 3"
   git remote add origin https://github.com/USUARIO/quetzalmart.git && git push -u origin main
   ```
   `.gitignore` ya excluye `.env`, `backups/` y los PDFs generados.
4. Lo ideal es que cada integrante entre con su **propio usuario**: *Ajustes → Usuarios → Nuevo*, con permisos
   de administrador en las apps que use. Así queda trazabilidad de quién hizo qué.
5. Antes de cambios grandes (por ejemplo, la carga del RPA) conviene sacar un respaldo: `bash scripts/backup.sh` en la EC2.

Si alguien quiere probar en su PC antes de tocar la EC2: `copy .env.example .env`, `docker compose up -d` y
`docker compose --profile seed run --rm seed`. Funciona en http://localhost:18069, con puertos que no chocan
con otros proyectos.

## 2. Qué NO tocar

- **No** borrar ni renombrar proveedores, materiales (`MAT-…`), empleados, cargos ni departamentos: las
  consultas SQL y el seed los buscan por nombre/código.
- **No** correr `docker compose down -v` en la EC2: borra la base de datos completa.
- **No** cambiar `report.url` (Ajustes → Técnico → Parámetros del sistema). Si se cambia, los PDF salen sin estilos.
- **No** usar los correos personales de los integrantes como remitente (lo pide el enunciado).

## 3. Pendientes por integrante (resumen; el detalle está en `PROMPT_SIGUIENTE_AGENTE.md`)

| Integrante | Rúbrica | Qué falta |
|---|---|---|
| 1 · Gestor documental | 1.27-1.29 | Menú **Documentos**: crear almacenamiento, carpetas y etiquetas/categorías, y subir ≥5 facturas de proveedor (sirven las de `facturas_pdf/compras/`), ≥5 contratos de outsourcing (proveedores con etiqueta *Outsourcing*) y ≥5 contratos de empleados. Filtrar por etiqueta |
| 2 · Google Analytics | 1.14-1.26, Manual 3 | Crear la propiedad GA4 y pegar el ID `G-…` en **Sitio web → Configuración → Ajustes → Google Analytics**. Odoo ya envía `view_item`, `add_to_cart` y `purchase`; **`begin_checkout` hay que agregarlo** (fragmento JS). Luego segmentos, audiencias, exploraciones y Manual 3 |
| 4 · Portal web, ventas, marketing | 1.01, 1.02, 1.10-1.13, 1.32-1.33 | Tema y páginas del sitio, productos publicados (con imágenes), impuestos y métodos de envío, pasarela de pago (Stripe/PayPal en modo prueba o Demo), 150 ventas + ≥8 cotizaciones a clientes (ya hay 12 a proveedores), servidor SMTP del proyecto y correo de compra + correo de campaña con asunto distinto |
| 5 · RPA + Manuales 1 y 2 | 1.30-1.31, 2.01-2.09 | Robot UiPath que lee las hojas `clientes` y `productos` y los carga a Odoo (se recomienda JSON-RPC, ver prompt). Manuales 1 y 2, usando `docs/INTEGRANTE3_ERP.md` y las plantillas de `carga_masiva/` |

## 4. Datos útiles

- Moneda **GTQ** · IVA **12 %**: impuestos `12%` de venta y de compra (localización l10n_gt). En las facturas se ven como "IVA 12%".
- Almacenes: `GT` QuetzalMart Guatemala (Central), `MX` QuetzalMart México, `SV` QuetzalMart El Salvador.
- Categoría para productos de venta (RPA / eCommerce): crear una nueva, por ejemplo `Alimentos y Bebidas`.
  **No** usar `Materiales de Sucursal`, que es solo de uso interno (`sale_ok = False`).
- Servidor de correo saliente: **Ajustes → Técnico → Servidores de correo saliente**. En AWS el puerto 25 está
  bloqueado, así que hay que usar 587 (STARTTLS) o 465 (SSL).
