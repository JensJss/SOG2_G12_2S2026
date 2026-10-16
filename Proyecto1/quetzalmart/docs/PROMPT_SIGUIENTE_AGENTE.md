# Prompts listos para el agente LLM de cada integrante

Cómo usarlo: copia el **CONTEXTO COMÚN** y agrega debajo el bloque de **tu** integrante. Adjunta también el
enunciado (`Proyecto_Segundo_Semestre_2026.pdf`), la rúbrica, `Distribucion.md` y esta carpeta del proyecto
(o el link del repo).

---

## CONTEXTO COMÚN (pegar siempre)

```text
Eres mi asistente técnico para el proyecto único de "Sistemas Organizacionales y Gerenciales 2"
(USAC, 2.º semestre 2026): la cadena de supermercados ficticia QuetzalMart (Guatemala, con sucursales
en México y El Salvador). Adjunto el enunciado, la rúbrica de calificación y la distribución de tareas.
Antes de hacer cambios, lee todo, aclara tus dudas dándome opciones concretas y trabaja sin romper lo existente.

ESTADO ACTUAL (lo dejó el Integrante 3, ya verificado):
- Repo/carpeta "quetzalmart" con docker-compose: Odoo 18 Community (imagen odoo:18.0) + PostgreSQL 16
  (postgres:16) en la MISMA VM, más nginx (perfil "proxy") en el puerto 80 para la EC2 de AWS.
  Lee README.md, docs/EC2_DESPLIEGUE.md, docs/TRASPASO_EQUIPO.md y docs/INTEGRANTE3_ERP.md.
- Producción = EC2 (http://IP_ELASTICA). Es la única fuente de verdad: trabajamos todos sobre esa
  instancia, que es la que se califica. Base de datos: "quetzalmart", usuario de BD "odoo".
  Consultas: docker compose exec db psql -U odoo -d quetzalmart
- En PC local (solo pruebas) Odoo corre en http://localhost:18069 y Postgres en 127.0.0.1:15432.
  NO uses los puertos 8069, 8072, 8080, 5432, 1025, 8025, 27017, 1433, 8070 ni 8090: están ocupados
  por otros proyectos que NO se deben tocar ni detener. Nunca corras "docker compose down -v" en la EC2.
- Idioma es_419, moneda GTQ, IVA 12 % (localización l10n_gt: impuestos "12%" de venta y compra).
- Empresa "QuetzalMart, S.A." con logo. Almacenes: GT "QuetzalMart Guatemala (Central)",
  MX "QuetzalMart México" y SV "QuetzalMart El Salvador".
- Módulos ya instalados: contacts, hr, hr_contract, purchase, purchase_stock, stock, account (+l10n_gt),
  sale_management, sale_stock, crm, website, website_sale, website_sale_stock, mass_mailing,
  mass_mailing_sale, mass_mailing_crm, base_automation y dms (OCA, en addons/). Hay módulos extra
  disponibles en el core sin instalar: payment_stripe, payment_paypal, payment_demo, payment_custom
  y delivery (ya es dependencia de website_sale).
- Datos ya cargados (NO borrar ni renombrar): 37 empleados, 8 cargos, 5 departamentos, 36 contratos,
  16 proveedores de materiales + 4 de outsourcing (etiqueta "Outsourcing"), 64 materiales en la categoría
  "Materiales de Sucursal / ..." (código MAT-XXX-nn, sale_ok=False), 105 compras confirmadas, recibidas
  y facturadas, 105 facturas de proveedor publicadas con PDF en facturas_pdf/compras/ y 12 solicitudes
  de cotización a proveedores.
- sql/consultas_calificacion.sql ya trae las consultas de TODA la rúbrica (incluidas las de mi parte)
  y un resumen de metas. Si agregas datos, verifica que el resumen los refleje.
- Para cargar datos por script, imita seed/seed.py (XML-RPC con librería estándar, idempotente,
  se ejecuta con el perfil "seed" del compose o con Python local apuntando a la URL de Odoo).
- Odoo 18: los nombres traducibles (productos, cargos, departamentos, etiquetas) son JSONB en SQL
  -> COALESCE(name->>'es_419', name->>'en_US'). Tipo de producto: type='consu' (Bienes) + is_storable=True
  para controlar inventario; type='service' para servicios.
- Correos: AWS bloquea el puerto 25; usa SMTP 587/465 con una cuenta DEL PROYECTO (nunca la personal de
  un integrante). En Odoo, Ajustes → Técnico → Servidores de correo saliente. La acción planificada
  "Mail: Email Queue Manager" corre cada 1 hora: bájala a 1 minuto para la calificación.
```

---

## INTEGRANTE 4 · Portal web, ventas y marketing CRM (siguiente en la lista)

```text
MI PARTE (Integrante 4). Rúbrica: 1.01 Ventas (150), 1.02 Cotizaciones (≥20 entre clientes y
proveedores; ya hay 12 a proveedores, faltan ≥8 a clientes, mejor 10+), 1.10 Sitio web con buena
presentación y login, 1.11 Productos con imagen, descripción y precio, 1.12 Carrito (agregar, eliminar,
impuestos, costo de envío), 1.13 Pago integrado, 1.32 Correo de compra con recibo/factura adjunta y
enviado desde un correo del sitio, 1.33 Correo de campaña de marketing original y vistoso, con asunto
distinto y recibido después del de compra.

Necesito que:
1. Diseñes el sitio (inicio, tienda, contacto) con la identidad de QuetzalMart: verde #007A4D y
   amarillo #E6A000. En el core solo viene theme_default; si quieres otro tema, los oficiales están en
   github.com/odoo/design-themes (rama 18.0) y se copian a addons/.
2. Configures la tienda: categorías públicas (ej. Abarrotes, Bebidas, Lácteos, Limpieza del hogar),
   productos publicados con imagen y descripción, impuesto de venta "12%", métodos de envío (tarifa fija
   y/o por zona) y una pasarela de pago en modo prueba (Stripe test o PayPal sandbox; Demo solo para
   pruebas internas). Coordina con el Integrante 5: el RPA también carga productos (hoja "productos") y
   clientes (hoja "clientes").
3. Cargues por script (XML-RPC, idempotente, como seed/seed.py) 150 ventas confirmadas con distintos
   productos y clientes, con fechas de 2026, y que la mayoría queden facturadas (para facturar usa el
   wizard sale.advance.payment.inv), más ≥10 cotizaciones a clientes en borrador/enviadas.
4. Configures el correo: servidor SMTP del proyecto, "Factura automática" (parámetro
   sale.automatic_invoice) para que al pagar en línea se envíe el recibo/factura en PDF, y una
   campaña de marketing (plantilla HTML vistosa con productos y promociones) que se envíe
   automáticamente DESPUÉS del correo de compra, con un asunto diferente. Propón la forma más confiable
   en Odoo 18 Community (por ejemplo, una regla automatizada de base_automation sobre la factura o el
   pedido que envíe la plantilla, o una lista de correo de mass_mailing) y pruébala de punta a punta.
5. Agregues a sql/consultas_calificacion.sql lo que haga falta y me des un guion para la simulación de
   compra en vivo: registro → carrito → pago → 2 correos.
```

---

## INTEGRANTE 1 · Gestor documental

```text
MI PARTE (Integrante 1). Rúbrica: 1.27 Gestor documental integrado a Odoo (3 pts), 1.28 Subir ≥5 facturas
de proveedores, ≥5 contratos de outsourcing y ≥5 contratos de empleados, 1.29 Organizar con etiquetas y
filtrar por etiquetas. Además apoyo en las secciones de los manuales sobre el gestor documental.

Ya está instalado el módulo OCA "dms" 18.0 (menú Documentos), y en addons/ también están dms_field y
hr_dms_field (sin instalar) por si conviene ligar documentos a empleados. Necesito que:
1. Configures dms: almacenamiento (Storage) en base de datos o adjuntos, grupos de acceso con los
   usuarios del equipo, una carpeta raíz "QuetzalMart" con subcarpetas "Facturas de Proveedores",
   "Contratos de Outsourcing" y "Contratos de Empleados" (y otras si aportan), categorías y etiquetas
   (por tipo, por sucursal GT/MX/SV, por año, por proveedor...).
2. Subas los documentos: facturas reales del sistema (PDFs en facturas_pdf/compras/), contratos de
   outsourcing con los 4 proveedores de la etiqueta "Outsourcing" (seguridad, limpieza, transporte, TI) y
   contratos laborales de empleados existentes (hay 36 contratos en Empleados → Contratos con salario y
   fecha de inicio; genera los PDF de los contratos con esos datos).
3. Demuestres el filtrado por etiquetas y categorías, y verifiques con la sección "GESTOR DOCUMENTAL"
   de sql/consultas_calificacion.sql (tablas dms_file, dms_tag, dms_file_tag_rel con columnas fid/tid).
4. Me prepares el texto y la lista de capturas para los manuales.
```

---

## INTEGRANTE 2 · Google Analytics 4 y Manual 3

```text
MI PARTE (Integrante 2). Rúbrica: 1.14 GA4 integrado al ERP, 1.15-1.18 eventos view_item, add_to_cart,
begin_checkout y purchase, 1.19-1.23 tasa de conversión, adquisición de usuarios, total de ingresos,
productos más vendidos y abandono del carrito, 1.24 3 segmentos de usuario y 5 de eventos,
1.25 2 exploraciones, 1.26 3 audiencias (≥1 personalizada; una de abandono de carrito) y 2.10-2.11
Manual 3 de inteligencia de negocios con gráficas.

Hechos verificados en el código de Odoo 18:
- El ID de medición (G-XXXX) se pone en Sitio web → Configuración → Ajustes → Google Analytics.
- website_sale ya envía por gtag: view_item (página de producto), add_to_cart y purchase (confirmación).
- begin_checkout NO lo envía Odoo (solo registra una vista virtual /stats/ecom/customer_checkout).
  Hay que agregarlo: con "Código <head> personalizado" del editor del sitio o, mejor, con un módulo
  pequeño en addons/ que herede la plantilla del checkout y llame a gtag('event','begin_checkout',
  {currency:'GTQ', value, items}) con los productos del carrito.
- Si se activa la barra de cookies del sitio, GA puede no disparar hasta que se acepten: tenlo en cuenta.
Necesito que:
1. Crees o configures la propiedad GA4 (flujo web con la URL de la EC2), la conectes y verifiques los 4
   eventos en DebugView/Tiempo real.
2. Implementes begin_checkout con items y moneda GTQ, y verifiques que purchase lleve value/currency/items.
3. Generes tráfico y compras de prueba durante varios días ANTES de la calificación (los informes de GA4
   tardan 24-48 h) y prepares los informes, segmentos, exploraciones y audiencias solicitados. El
   auxiliar generará interacciones en la calificación y hay que mostrarlas.
4. Redactes el Manual 3 con gráficas e interpretación de negocio: conversión, embudo, abandono,
   productos y adquisición, más recomendaciones.
```

---

## INTEGRANTE 5 · RPA UiPath y Manuales 1 y 2

```text
MI PARTE (Integrante 5). Rúbrica: 1.30 El robot carga los clientes al ERP durante la calificación, 1.31 El
robot carga los productos y 2.01-2.09 Manual 1 (instalación, módulos, carga masiva con capturas, RPA y
sus ventajas) y Manual 2 (diagramas de flujo: UiPath, compras a proveedores, ventas, flujo completo de la
empresa desde recepción hasta venta —recepción, almacenamiento por sector, productos defectuosos,
control de inventario, empaque, control de calidad— y flujo del cliente web/tienda).

Detalles del enunciado: se recibe una carpeta con jerarquía poco práctica (clientes, proveedores, reclamos,
registro, productos, más guion y descripción) y archivos Excel con varias hojas. Solo interesan los archivos
que tengan hojas llamadas "clientes" o "productos".
 - clientes: Name, Company Type, Related Company, Email, Phone, Street, Street2, City, State, Zip,
   Country, Tax ID, Website, Tags, Reference, Notes
 - productos: ID Externo, Name, Product Type, Internal Reference, Barcode, Sales Price, Cost, Weight,
   Sales Description, Product Values, Cantidad a la mano, Está publicado
Lo cargado debe verse en el sitio web y por SQL (secciones "RPA" de sql/consultas_calificacion.sql).

Sugerencias técnicas (Odoo 18):
- Desde UiPath, usar HTTP Request a POST http://IP/jsonrpc con
  {"jsonrpc":"2.0","method":"call","params":{"service":"object","method":"execute_kw",
   "args":["quetzalmart", UID, "PASSWORD", "<modelo>", "<metodo>", [args], {kwargs}]}}
  (UID con service "common", method "login"). Para ID Externo conviene el método "load" de
  product.template con la columna "id": así queda en ir_model_data, igual que el importador de Odoo.
- Mapeo clientes → res.partner: name, company_type ('company'/'person'), parent_id (empresa relacionada),
  email, phone, street, street2, city, state_id, zip, country_id, vat, website, category_id (etiquetas),
  ref, comment; customer_rank=1.
- Mapeo productos → product.template: name, type ('consu'/'service'/'combo') + is_storable,
  default_code, barcode, list_price, standard_price, weight, description_sale, is_published,
  public_categ_ids; "Cantidad a la mano" con stock.quant (inventory_quantity en la ubicación de stock
  del almacén GT + action_apply_inventory); "Product Values" → atributos/valores (decidir con el equipo).
- Que sea idempotente: buscar por correo/nombre o por ID externo antes de crear, para no duplicar.
Para el Manual 1, usa docs/INTEGRANTE3_ERP.md, las plantillas de carga_masiva/ (Odoo: Importar
registros) y docs/EC2_DESPLIEGUE.md (instalación).
```
