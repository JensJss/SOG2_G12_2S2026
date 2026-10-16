-- =============================================================================
--  QuetzalMart - Consultas SQL para la calificación (Odoo 18 / PostgreSQL 16)
--  Base: quetzalmart     Usuario: odoo
--
--  Cómo ejecutarlas (en la EC2 o en la PC):
--    docker compose exec db psql -U odoo -d quetzalmart -f /sql/consultas_calificacion.sql
--  O una por una:   docker compose exec db psql -U odoo -d quetzalmart
--  O con Adminer / DBeaver (ver README).
--
--  Nota: en Odoo 18 los nombres traducibles (cargos, departamentos, productos)
--  son JSONB -> se leen con COALESCE(name->>'es_419', name->>'en_US').
-- =============================================================================
\pset pager off
\pset null '-'

\echo '================  RESUMEN GENERAL (todas las metas de la rúbrica)  ================'
SELECT * FROM (VALUES
  ('1.01 Ventas confirmadas (>=150)',
      (SELECT count(*) FROM sale_order WHERE state = 'sale')::int, 150),
  ('1.01 Clientes distintos con ventas',
      (SELECT count(DISTINCT partner_id) FROM sale_order WHERE state = 'sale')::int, 2),
  ('1.02 Cotizaciones a clientes (draft/sent)',
      (SELECT count(*) FROM sale_order WHERE state IN ('draft','sent'))::int, 0),
  ('1.02 Cotizaciones a proveedores (RFQ)',
      (SELECT count(*) FROM purchase_order WHERE state IN ('draft','sent'))::int, 0),
  ('1.02 Total cotizaciones clientes+proveedores (>=20)',
      ((SELECT count(*) FROM sale_order WHERE state IN ('draft','sent'))
     + (SELECT count(*) FROM purchase_order WHERE state IN ('draft','sent')))::int, 20),
  ('1.03 Empleados activos (>=35)',
      (SELECT count(*) FROM hr_employee WHERE active)::int, 35),
  ('1.04 Cargos (>=6)',
      (SELECT count(*) FROM hr_job)::int, 6),
  ('1.05 Departamentos (>=5)',
      (SELECT count(*) FROM hr_department WHERE active)::int, 5),
  ('1.06 Compras confirmadas (>=100)',
      (SELECT count(*) FROM purchase_order WHERE state IN ('purchase','done'))::int, 100),
  ('1.06 Compras con factura publicada (>=100)',
      (SELECT count(DISTINCT po.id) FROM purchase_order po
         JOIN purchase_order_line pol ON pol.order_id = po.id
         JOIN account_move_line aml ON aml.purchase_line_id = pol.id
         JOIN account_move am ON am.id = aml.move_id AND am.state = 'posted'
        WHERE po.state IN ('purchase','done'))::int, 100),
  ('1.07 Materiales de sucursal (>=60)',
      (SELECT count(*) FROM product_template pt JOIN product_category pc ON pc.id = pt.categ_id
        WHERE pc.complete_name LIKE 'Materiales de Sucursal%' AND pt.active)::int, 60),
  ('1.08 Facturas publicadas compras+ventas (>=50)',
      (SELECT count(*) FROM account_move WHERE move_type IN ('in_invoice','out_invoice') AND state = 'posted')::int, 50),
  ('1.27 Archivos en gestor documental (>=15)',
      (SELECT count(*) FROM dms_file WHERE active)::int, 15)
) AS t(criterio, valor, minimo)
;

-- =============================================================================
\echo '================  1.03 EMPLEADOS (>= 35)  ================'
SELECT e.id,
       e.name                                                   AS empleado,
       COALESCE(j.name->>'es_419', j.name->>'en_US')            AS cargo,
       COALESCE(d.name->>'es_419', d.name->>'en_US')            AS departamento,
       wl.name                                                  AS sucursal,
       e.work_email                                             AS correo,
       m.name                                                   AS jefe_inmediato
FROM hr_employee e
LEFT JOIN hr_job j            ON j.id = e.job_id
LEFT JOIN hr_department d     ON d.id = e.department_id
LEFT JOIN hr_work_location wl ON wl.id = e.work_location_id
LEFT JOIN hr_employee m       ON m.id = e.parent_id
WHERE e.active
ORDER BY departamento, cargo, empleado;

SELECT count(*) AS total_empleados FROM hr_employee WHERE active;

-- =============================================================================
\echo '================  1.04 CARGOS (>= 6)  ================'
SELECT j.id,
       COALESCE(j.name->>'es_419', j.name->>'en_US')     AS cargo,
       COALESCE(d.name->>'es_419', d.name->>'en_US')     AS departamento,
       (SELECT count(*) FROM hr_employee e WHERE e.job_id = j.id AND e.active) AS empleados
FROM hr_job j
LEFT JOIN hr_department d ON d.id = j.department_id
ORDER BY cargo;

-- =============================================================================
\echo '================  1.05 DEPARTAMENTOS (>= 5)  ================'
SELECT d.id,
       COALESCE(d.name->>'es_419', d.name->>'en_US')     AS departamento,
       m.name                                            AS jefe,
       (SELECT count(*) FROM hr_employee e WHERE e.department_id = d.id AND e.active) AS empleados
FROM hr_department d
LEFT JOIN hr_employee m ON m.id = d.manager_id
WHERE d.active
ORDER BY departamento;

\echo '----- Empleados por departamento y sucursal -----'
SELECT COALESCE(d.name->>'es_419', d.name->>'en_US') AS departamento,
       count(*) FILTER (WHERE wl.name LIKE '%Guatemala%')   AS guatemala,
       count(*) FILTER (WHERE wl.name LIKE '%xico%')        AS mexico,
       count(*) FILTER (WHERE wl.name LIKE '%Salvador%')    AS el_salvador,
       count(*)                                             AS total
FROM hr_employee e
JOIN hr_department d ON d.id = e.department_id
LEFT JOIN hr_work_location wl ON wl.id = e.work_location_id
WHERE e.active
GROUP BY 1 ORDER BY 1;

\echo '----- Contratos laborales -----'
SELECT c.name AS contrato, e.name AS empleado, c.wage AS salario_gtq, c.date_start AS inicio, c.state AS estado
FROM hr_contract c JOIN hr_employee e ON e.id = c.employee_id
ORDER BY e.name;

-- =============================================================================
\echo '================  1.06 COMPRAS (>= 100) Y SUS FACTURAS  ================'
SELECT po.name                              AS orden_compra,
       po.date_order::date                   AS fecha,
       p.name                                AS proveedor,
       w.name                                AS sucursal_destino,
       po.amount_total                       AS total_gtq,
       po.state                              AS estado,
       po.invoice_status                     AS estado_facturacion,
       string_agg(DISTINCT am.name, ', ')    AS factura,
       string_agg(DISTINCT am.payment_state, ', ') AS pago
FROM purchase_order po
JOIN res_partner p              ON p.id = po.partner_id
LEFT JOIN stock_picking_type spt ON spt.id = po.picking_type_id
LEFT JOIN stock_warehouse w     ON w.id = spt.warehouse_id
LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
LEFT JOIN account_move_line aml ON aml.purchase_line_id = pol.id
LEFT JOIN account_move am       ON am.id = aml.move_id AND am.state = 'posted'
WHERE po.state IN ('purchase','done')
GROUP BY po.id, p.name, w.name
ORDER BY po.date_order;

\echo '----- Totales de compras -----'
SELECT count(*)                                         AS compras_confirmadas,
       count(*) FILTER (WHERE invoice_status = 'invoiced') AS compras_facturadas,
       round(sum(amount_untaxed), 2)                    AS subtotal_gtq,
       round(sum(amount_total), 2)                      AS total_con_iva_gtq
FROM purchase_order WHERE state IN ('purchase','done');

\echo '----- Compras por sucursal -----'
SELECT w.name AS sucursal, count(*) AS compras, round(sum(po.amount_total), 2) AS total_gtq
FROM purchase_order po
JOIN stock_picking_type spt ON spt.id = po.picking_type_id
JOIN stock_warehouse w ON w.id = spt.warehouse_id
WHERE po.state IN ('purchase','done')
GROUP BY w.name ORDER BY compras DESC;

\echo '----- Compras por proveedor -----'
SELECT p.name AS proveedor, count(*) AS compras, round(sum(po.amount_total), 2) AS total_gtq
FROM purchase_order po JOIN res_partner p ON p.id = po.partner_id
WHERE po.state IN ('purchase','done')
GROUP BY p.name ORDER BY total_gtq DESC;

\echo '----- Recepciones de mercadería (inventario) -----'
SELECT sp.name AS recepcion, sp.origin AS orden_compra, sp.state, sp.date_done::date AS fecha_recepcion,
       w.name AS almacen
FROM stock_picking sp
JOIN stock_picking_type spt ON spt.id = sp.picking_type_id AND spt.code = 'incoming'
JOIN stock_warehouse w ON w.id = spt.warehouse_id
ORDER BY sp.date_done;

-- =============================================================================
\echo '================  1.07 MATERIALES PARA LAS SUCURSALES (>= 60)  ================'
SELECT pt.default_code                                   AS codigo,
       COALESCE(pt.name->>'es_419', pt.name->>'en_US')   AS material,
       pc.complete_name                                  AS categoria,
       (SELECT min(si.price) FROM product_supplierinfo si WHERE si.product_tmpl_id = pt.id) AS costo_proveedor_gtq,
       (SELECT count(*) FROM product_supplierinfo si WHERE si.product_tmpl_id = pt.id)      AS proveedores,
       COALESCE((SELECT sum(q.quantity) FROM stock_quant q
                   JOIN product_product pp ON pp.id = q.product_id
                   JOIN stock_location l ON l.id = q.location_id AND l.usage = 'internal'
                  WHERE pp.product_tmpl_id = pt.id), 0)                                     AS existencia
FROM product_template pt
JOIN product_category pc ON pc.id = pt.categ_id
WHERE pc.complete_name LIKE 'Materiales de Sucursal%' AND pt.active
ORDER BY pt.default_code;

\echo '----- Materiales por categoría -----'
SELECT pc.complete_name AS categoria, count(*) AS materiales
FROM product_template pt JOIN product_category pc ON pc.id = pt.categ_id
WHERE pc.complete_name LIKE 'Materiales de Sucursal%' AND pt.active
GROUP BY pc.complete_name ORDER BY 1;

\echo '----- Existencia de materiales por sucursal -----'
SELECT w.name AS sucursal, count(DISTINCT pp.product_tmpl_id) AS materiales_distintos,
       round(sum(q.quantity), 0) AS unidades
FROM stock_quant q
JOIN stock_location l    ON l.id = q.location_id AND l.usage = 'internal'
JOIN stock_warehouse w   ON w.id = l.warehouse_id
JOIN product_product pp  ON pp.id = q.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pt.default_code LIKE 'MAT-%'
GROUP BY w.name ORDER BY 1;

-- =============================================================================
\echo '================  1.08 / 1.09 FACTURAS (>= 50)  ================'
SELECT am.name                    AS factura,
       CASE am.move_type WHEN 'in_invoice' THEN 'Compra (proveedor)'
                         WHEN 'out_invoice' THEN 'Venta (cliente)' END AS tipo,
       am.invoice_date            AS fecha,
       p.name                     AS contacto,
       am.invoice_origin          AS origen,
       am.ref                     AS referencia,
       am.amount_untaxed          AS subtotal,
       am.amount_tax              AS iva,
       am.amount_total            AS total,
       am.payment_state           AS estado_pago
FROM account_move am
JOIN res_partner p ON p.id = am.partner_id
WHERE am.move_type IN ('in_invoice','out_invoice') AND am.state = 'posted'
ORDER BY am.invoice_date, am.name;

\echo '----- Totales de facturas por tipo -----'
SELECT move_type AS tipo, count(*) AS facturas, round(sum(amount_total), 2) AS total_gtq,
       count(*) FILTER (WHERE payment_state IN ('paid','in_payment')) AS pagadas
FROM account_move
WHERE move_type IN ('in_invoice','out_invoice') AND state = 'posted'
GROUP BY move_type;

\echo '----- 1.09 Últimas facturas (las generadas durante la calificación aparecen arriba) -----'
SELECT am.name, am.move_type, p.name AS contacto, am.amount_total, am.create_date
FROM account_move am JOIN res_partner p ON p.id = am.partner_id
WHERE am.move_type IN ('in_invoice','out_invoice')
ORDER BY am.create_date DESC LIMIT 10;

-- =============================================================================
--  SECCIONES DE LOS DEMÁS INTEGRANTES (devuelven 0 filas hasta que carguen sus datos)
-- =============================================================================
\echo '================  1.01 VENTAS (>= 150)  [Integrante 4]  ================'
SELECT so.name AS venta, so.date_order::date AS fecha, p.name AS cliente,
       so.amount_total AS total, so.state,
       (SELECT count(DISTINCT sol.product_id) FROM sale_order_line sol
         WHERE sol.order_id = so.id AND sol.display_type IS NULL) AS productos_distintos
FROM sale_order so JOIN res_partner p ON p.id = so.partner_id
WHERE so.state = 'sale'
ORDER BY so.date_order;

SELECT count(*) AS ventas, count(DISTINCT partner_id) AS clientes_distintos,
       (SELECT count(DISTINCT sol.product_id) FROM sale_order_line sol JOIN sale_order s ON s.id = sol.order_id
         WHERE s.state = 'sale' AND sol.display_type IS NULL) AS productos_distintos
FROM sale_order WHERE state = 'sale';

\echo '================  1.02 COTIZACIONES A CLIENTES Y PROVEEDORES (>= 20)  ================'
SELECT 'Cliente' AS tipo, so.name AS cotizacion, p.name AS contacto, so.date_order::date AS fecha,
       so.amount_total AS total, so.state
FROM sale_order so JOIN res_partner p ON p.id = so.partner_id
WHERE so.state IN ('draft','sent')
UNION ALL
SELECT 'Proveedor', po.name, p.name, po.date_order::date, po.amount_total, po.state
FROM purchase_order po JOIN res_partner p ON p.id = po.partner_id
WHERE po.state IN ('draft','sent')
ORDER BY tipo, fecha;

\echo '================  RPA: CLIENTES (hoja "clientes")  [Integrante 5]  ================'
SELECT p.id, p.name, CASE WHEN p.is_company THEN 'Company' ELSE 'Individual' END AS company_type,
       parent.name AS related_company, p.email, p.phone, p.street, p.street2, p.city,
       st.name AS state, p.zip, c.name->>'en_US' AS country, p.vat AS tax_id, p.website, p.ref AS reference,
       p.create_date
FROM res_partner p
LEFT JOIN res_partner parent ON parent.id = p.parent_id
LEFT JOIN res_country_state st ON st.id = p.state_id
LEFT JOIN res_country c ON c.id = p.country_id
WHERE p.active
  AND p.supplier_rank = 0                                                        -- no proveedores
  AND p.id NOT IN (SELECT partner_id FROM res_users)                             -- no usuarios internos/portal
  AND p.id NOT IN (SELECT partner_id FROM res_company)                           -- no la empresa
  AND p.id NOT IN (SELECT work_contact_id FROM hr_employee WHERE work_contact_id IS NOT NULL) -- no empleados
  AND COALESCE(p.parent_id, 0) NOT IN (SELECT partner_id FROM res_company)       -- no sucursales
ORDER BY p.create_date DESC;

SELECT count(*) AS total_clientes FROM res_partner p
WHERE p.active AND p.supplier_rank = 0
  AND p.id NOT IN (SELECT partner_id FROM res_users)
  AND p.id NOT IN (SELECT partner_id FROM res_company)
  AND p.id NOT IN (SELECT work_contact_id FROM hr_employee WHERE work_contact_id IS NOT NULL)
  AND COALESCE(p.parent_id, 0) NOT IN (SELECT partner_id FROM res_company);

\echo '================  RPA: PRODUCTOS (hoja "productos")  [Integrante 5]  ================'
SELECT imd.module || '.' || imd.name                 AS id_externo,
       COALESCE(pt.name->>'es_419', pt.name->>'en_US') AS name,
       pt.type AS product_type, pt.is_storable, pt.default_code AS internal_reference,
       pp.barcode, pt.list_price AS sales_price,
       COALESCE((pp.standard_price->>(SELECT id::text FROM res_company ORDER BY id LIMIT 1))::numeric, 0) AS cost,
       pt.weight, COALESCE(pt.description_sale->>'es_419', pt.description_sale->>'en_US') AS sales_description,
       pt.is_published AS esta_publicado,
       COALESCE((SELECT sum(q.quantity) FROM stock_quant q JOIN stock_location l ON l.id = q.location_id
                  WHERE q.product_id = pp.id AND l.usage = 'internal'), 0) AS cantidad_a_la_mano
FROM product_template pt
JOIN product_product pp ON pp.product_tmpl_id = pt.id
LEFT JOIN ir_model_data imd ON imd.model = 'product.template' AND imd.res_id = pt.id
WHERE pt.sale_ok AND pt.active
ORDER BY pt.create_date DESC;

\echo '================  1.27-1.29 GESTOR DOCUMENTAL (OCA dms)  [Integrante 1]  ================'
SELECT f.name AS archivo, d.name AS carpeta, COALESCE(cat.name->>'es_419', cat.name->>'en_US') AS categoria,
       string_agg(COALESCE(t.name->>'es_419', t.name->>'en_US'), ', ') AS etiquetas, f.create_date::date AS subido
FROM dms_file f
JOIN dms_directory d ON d.id = f.directory_id
LEFT JOIN dms_category cat ON cat.id = f.category_id
LEFT JOIN dms_file_tag_rel r ON r.fid = f.id
LEFT JOIN dms_tag t ON t.id = r.tid
WHERE f.active
GROUP BY f.id, d.name, cat.name
ORDER BY carpeta, archivo;

\echo '----- Archivos por etiqueta (filtrado por etiquetas) -----'
SELECT COALESCE(t.name->>'es_419', t.name->>'en_US') AS etiqueta, count(*) AS archivos
FROM dms_tag t JOIN dms_file_tag_rel r ON r.tid = t.id JOIN dms_file f ON f.id = r.fid AND f.active
GROUP BY 1 ORDER BY 1;

\echo '================  MARKETING  [Integrante 4]  ================'
SELECT m.subject AS asunto, m.state, m.sent_date, m.create_date::date
FROM mailing_mailing m ORDER BY m.create_date DESC;
