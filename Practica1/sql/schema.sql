

-- 0. Esquema dedicado (opcional, facilita permisos/orden en RDS compartido)
CREATE SCHEMA IF NOT EXISTS ventas;
SET search_path TO ventas, public;

-- =====================================================================
-- 1. CATÁLOGOS (tablas de dominio / lookup)
-- =====================================================================

CREATE TABLE IF NOT EXISTS ventas.cat_genero (
    id_genero   SMALLINT PRIMARY KEY,
    descripcion VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas.cat_metodo_pago (
    id_metodo_pago SMALLINT PRIMARY KEY,
    descripcion     VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas.cat_navegador (
    id_navegador SMALLINT PRIMARY KEY,
    descripcion  VARCHAR(30) NOT NULL
);

-- Datos fijos de catálogo según el enunciado de la práctica
INSERT INTO ventas.cat_genero (id_genero, descripcion) VALUES
    (0, 'Masculino'),
    (1, 'Femenino')
ON CONFLICT (id_genero) DO NOTHING;

INSERT INTO ventas.cat_metodo_pago (id_metodo_pago, descripcion) VALUES
    (0, 'Efectivo'),
    (1, 'Tarjeta de Crédito'),
    (2, 'Tarjeta de Débito')
ON CONFLICT (id_metodo_pago) DO NOTHING;

INSERT INTO ventas.cat_navegador (id_navegador, descripcion) VALUES
    (0, 'Tienda Física'),
    (1, 'Navegador 1'),
    (2, 'Navegador 2'),
    (3, 'Navegador 3'),
    (4, 'Navegador 4')
ON CONFLICT (id_navegador) DO NOTHING;

-- =====================================================================
-- 2. CLIENTES
--    Atributos "propios" del cliente (nivel agregado en el CSV origen)
-- =====================================================================

CREATE TABLE IF NOT EXISTS ventas.clientes (
    id_cliente   INTEGER PRIMARY KEY,
    edad         SMALLINT NOT NULL CHECK (edad BETWEEN 0 AND 120),
    id_genero    SMALLINT NOT NULL REFERENCES ventas.cat_genero(id_genero),
    venta_total  NUMERIC(12,2) NOT NULL CHECK (venta_total >= 0),
    n_compras    INTEGER NOT NULL CHECK (n_compras >= 0),
    creado_en    TIMESTAMP NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMP NOT NULL DEFAULT now()
);

-- =====================================================================
-- 3. COMPRAS
--    Una fila por transacción. Hoy 1:1 con clientes (una compra por
--    cliente en el CSV), pero el modelo soporta 1:N a futuro.
-- =====================================================================

CREATE TABLE IF NOT EXISTS ventas.compras (
    id_compra       BIGSERIAL PRIMARY KEY,
    id_cliente      INTEGER NOT NULL REFERENCES ventas.clientes(id_cliente),
    fecha_compra    DATE NOT NULL,
    monto_compra    NUMERIC(12,3) NOT NULL CHECK (monto_compra >= 0),
    id_metodo_pago  SMALLINT NOT NULL REFERENCES ventas.cat_metodo_pago(id_metodo_pago),
    tiempo_sitio    INTEGER NOT NULL CHECK (tiempo_sitio >= 0), -- segundos en sitio/tienda
    id_navegador    SMALLINT NOT NULL REFERENCES ventas.cat_navegador(id_navegador),
    boletin         BOOLEAN NOT NULL DEFAULT FALSE,
    vale            BOOLEAN NOT NULL DEFAULT FALSE,
    origen_carga    VARCHAR(50) NOT NULL DEFAULT 'csv_2021', -- trazabilidad de origen del dato
    creado_en       TIMESTAMP NOT NULL DEFAULT now()
);

-- =====================================================================
-- 4. ÍNDICES (soporte a los análisis de tendencias/segmentación)
-- =====================================================================

CREATE INDEX IF NOT EXISTS idx_compras_id_cliente   ON ventas.compras(id_cliente);
CREATE INDEX IF NOT EXISTS idx_compras_fecha         ON ventas.compras(fecha_compra);
CREATE INDEX IF NOT EXISTS idx_compras_metodo_pago   ON ventas.compras(id_metodo_pago);
CREATE INDEX IF NOT EXISTS idx_compras_navegador     ON ventas.compras(id_navegador);
CREATE INDEX IF NOT EXISTS idx_compras_boletin_vale  ON ventas.compras(boletin, vale);
CREATE INDEX IF NOT EXISTS idx_clientes_genero       ON ventas.clientes(id_genero);
CREATE INDEX IF NOT EXISTS idx_clientes_edad         ON ventas.clientes(edad);

-- =====================================================================
-- 5. VISTA DE CONVENIENCIA
--    Desnormalizada, con etiquetas legibles. Pensada para el equipo de
--    Análisis (Integrante 2/3) y para el agente de IA / MCP Server, que
--    podrán hacer "SELECT * FROM ventas.vw_ventas" sin JOINs manuales.
-- =====================================================================

CREATE OR REPLACE VIEW ventas.vw_ventas AS
SELECT
    co.id_compra,
    cl.id_cliente,
    cl.edad,
    g.descripcion   AS genero,
    cl.venta_total,
    cl.n_compras,
    co.fecha_compra,
    EXTRACT(MONTH FROM co.fecha_compra)::INT AS mes_compra,
    EXTRACT(YEAR  FROM co.fecha_compra)::INT AS anio_compra,
    co.monto_compra,
    mp.descripcion  AS metodo_pago,
    co.tiempo_sitio,
    nv.descripcion  AS navegador,
    co.boletin,
    co.vale
FROM ventas.compras co
JOIN ventas.clientes cl       ON cl.id_cliente = co.id_cliente
JOIN ventas.cat_genero g      ON g.id_genero = cl.id_genero
JOIN ventas.cat_metodo_pago mp ON mp.id_metodo_pago = co.id_metodo_pago
JOIN ventas.cat_navegador nv  ON nv.id_navegador = co.id_navegador;

