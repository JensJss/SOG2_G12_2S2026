# Integrante 3 · ERP administrativo (Empleados, Compras, Materiales, Facturas)

Todo se carga con `docker compose --profile seed run --rm seed` (ver README). Los datos son ficticios
pero coherentes: empresa **QuetzalMart, S.A.** (NIT 9876543-2), moneda **GTQ**, **IVA 12 %** (localización
`l10n_gt`) y 3 sucursales: **Guatemala (Central)**, **México** y **El Salvador**, cada una con su almacén
y su ubicación de trabajo.

## 1. Qué hay y dónde verlo en Odoo (menús en español)

| Rúbrica | Dato | Dónde verlo |
|---|---|---|
| 1.03 | 37 empleados (36 + admin) con cargo, departamento, sucursal, jefe, correo, teléfono, DPI y contrato | **Empleados** (vista Kanban/Lista; agrupar por *Departamento* o *Ubicación de trabajo*) · Organigrama en la ficha |
| 1.04 | 8 cargos: Gerente General, Contador General, Gerente de Sucursal, Cajero, Agente de Compras, Bodeguero, Ejecutivo de Ventas, Analista de Marketing Digital | **Empleados → Configuración → Puestos de trabajo** |
| 1.05 | 5 departamentos: Dirección General y Finanzas, Compras y Logística, Operaciones de Sucursal, Ventas y Atención al Cliente, Marketing y Tecnología | **Empleados → Departamentos** |
| — | 36 contratos laborales en curso, con salario en GTQ | **Empleados → Contratos** |
| 1.06 | 105 compras confirmadas, recibidas en bodega y facturadas: 93 de materiales y 12 de servicios de outsourcing | **Compras → Pedidos → Órdenes de compra** (columna *Estado de facturación* = Totalmente facturado) |
| 1.06 | 105 facturas de proveedor publicadas: unas 84 pagadas y el resto pendientes | **Facturación → Proveedores → Facturas** (*Facturas de proveedores*) · botón *Facturas* dentro de cada compra |
| 1.07 | 64 materiales en 8 categorías (`Materiales de Sucursal / …`), con código `MAT-XXX-nn`, proveedor y existencias por sucursal | **Compras → Productos → Productos** (filtrar por categoría) · **Inventario → Reportes → Existencias** |
| 1.08 | 105 PDF de facturas | Carpeta `facturas_pdf/compras/` + `facturas_pdf/indice_facturas.csv` |
| 1.02 | 12 solicitudes de cotización a proveedores (estado *Solicitud de cotización*) | **Compras → Pedidos → Solicitudes de cotización** |
| — | 16 proveedores de materiales + 4 de outsourcing (seguridad, limpieza, transporte, TI), con etiqueta | **Compras → Pedidos → Proveedores** |

## 2. Guion para la calificación en vivo (1.06 / 1.09 "Genera facturas durante la calificación")

**Compra → recepción → factura (2-3 min):**
1. **Compras → Nuevo**. Proveedor: *Ferretería El Volcán, S.A.* · Entregar a: *QuetzalMart México: Recepciones*.
2. Agregar producto `MAT-MAN-01 Foco LED 18 W`, cantidad 20 → **Confirmar pedido**.
3. Botón **Recepción** → **Validar** (entra al inventario de la sucursal).
4. Volver a la compra → **Crear factura** → poner *Fecha de factura* y *Referencia* (n.º de factura del proveedor) → **Confirmar**.
5. **Imprimir → Factura** (PDF con el logo de QuetzalMart). Opcional: **Registrar pago**.

**Factura de venta (si el auxiliar la pide):** **Facturación → Clientes → Facturas → Nuevo** → cliente,
producto, cantidad → **Confirmar** → **Imprimir**.

**Agregar las nuevas facturas a la carpeta de PDFs:**
```bash
docker compose --profile seed run --rm --entrypoint python3 seed -u /seed/export_invoices.py
```
Solo descarga las facturas nuevas y actualiza `indice_facturas.csv`.

**Mostrarlo en SQL** (aparecen arriba, ordenadas por fecha de creación):
```sql
SELECT am.name, am.move_type, p.name AS contacto, am.amount_total, am.create_date
FROM account_move am JOIN res_partner p ON p.id = am.partner_id
WHERE am.move_type IN ('in_invoice','out_invoice')
ORDER BY am.create_date DESC LIMIT 10;
```

## 3. Consultas SQL (requisito previo: "Lleva preparadas las consultas SQL")

Archivo: `sql/consultas_calificacion.sql`. Ejecutar todo:
```bash
docker compose exec db psql -U odoo -d quetzalmart -f /sql/consultas_calificacion.sql
```
Empieza con un **RESUMEN** que muestra, por cada criterio de la rúbrica, el valor actual y el mínimo exigido.
Después vienen las secciones 1.03, 1.04, 1.05, 1.06 (compras + factura + estado de pago + sucursal),
1.07 (materiales + existencias por sucursal), 1.08/1.09 (facturas) y las de los otros integrantes.

Tablas clave de Odoo 18:

| Concepto | Tabla | Nota |
|---|---|---|
| Empleados | `hr_employee` | `name` es texto |
| Cargos / Departamentos | `hr_job` / `hr_department` | `name` es **JSONB** → `name->>'es_419'` |
| Contratos | `hr_contract` | `state = 'open'` en curso |
| Compras | `purchase_order`, `purchase_order_line` | `state IN ('purchase','done')` = confirmadas |
| Facturas | `account_move` | `move_type = 'in_invoice'` proveedor, `'out_invoice'` cliente, `state = 'posted'` |
| Relación compra ↔ factura | `account_move_line.purchase_line_id` | |
| Materiales | `product_template` + `product_category` | `complete_name LIKE 'Materiales de Sucursal%'` |
| Existencias | `stock_quant` + `stock_location` + `stock_warehouse` | `usage = 'internal'` |
| Recepciones | `stock_picking` (+ `stock_picking_type.code = 'incoming'`) | |

## 4. Para el Manual 1 (secciones 2 y 3: lo coordina el Integrante 5)

- **Carga masiva por módulo:** en `carga_masiva/` hay plantillas Excel con los encabezados que acepta
  el importador de Odoo (*Favoritos → Importar registros*). Los archivos `datos_*.xlsx` documentan lo que ya
  está cargado. Los `demo_*.xlsx` traen pocos registros **nuevos** para tomar capturas importando de verdad
  sin duplicar nada.
- **Capturas sugeridas:** lista de empleados agrupada por departamento, organigrama, puestos de trabajo,
  una compra con su recepción y su factura (botones inteligentes arriba a la derecha), la lista de facturas
  de proveedor, un PDF de factura, la lista de materiales por categoría y las existencias por almacén.
- **Flujo de compra (para el diagrama del Manual 2):** solicitud de cotización → orden de compra confirmada
  → recepción en el almacén de la sucursal (control de cantidad) → factura de proveedor (IVA 12 %) →
  pago → la factura queda archivada en PDF y en el gestor documental.
