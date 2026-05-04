-- ms-pedidos (PED) - Inicialización PostgreSQL (psql)
-- Crea la base de datos y las tablas requeridas.

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', 'pedidos', 'pedidos123')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'pedidos')\gexec

SELECT format('CREATE DATABASE %I OWNER %I', 'ms_pedidos', 'pedidos')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ms_pedidos')\gexec

ALTER DATABASE ms_pedidos OWNER TO pedidos;
GRANT ALL PRIVILEGES ON DATABASE ms_pedidos TO pedidos;

\connect ms_pedidos

GRANT CREATE ON SCHEMA public TO pedidos;
SET ROLE pedidos;

CREATE TABLE IF NOT EXISTS ped_pedidos (
  id SERIAL PRIMARY KEY,
  numero_pedido VARCHAR(30) NOT NULL UNIQUE,
  solicitante_id BIGINT NOT NULL,
  proveedor_id BIGINT NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
  fecha_solicitud TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fecha_aprobacion TIMESTAMPTZ NULL,
  fecha_recepcion TIMESTAMPTZ NULL,
  monto_total NUMERIC(15,2) NOT NULL DEFAULT 0.00,
  observaciones TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_pedidos_estado CHECK (estado IN ('borrador','enviado','aprobado','en_proceso','recibido_parcial','recibido','cancelado'))
);

CREATE INDEX IF NOT EXISTS ix_ped_pedidos_id ON ped_pedidos (id);
CREATE INDEX IF NOT EXISTS ix_ped_pedidos_numero_pedido ON ped_pedidos (numero_pedido);
CREATE INDEX IF NOT EXISTS ix_ped_pedidos_solicitante_id ON ped_pedidos (solicitante_id);
CREATE INDEX IF NOT EXISTS ix_ped_pedidos_proveedor_id ON ped_pedidos (proveedor_id);
CREATE INDEX IF NOT EXISTS ix_ped_pedidos_estado ON ped_pedidos (estado);
CREATE INDEX IF NOT EXISTS ix_ped_pedidos_fecha_solicitud ON ped_pedidos (fecha_solicitud);

CREATE TABLE IF NOT EXISTS ped_items (
  id SERIAL PRIMARY KEY,
  pedido_id INTEGER NOT NULL REFERENCES ped_pedidos(id) ON DELETE CASCADE,
  activo_id BIGINT NOT NULL,
  descripcion TEXT NOT NULL,
  cantidad_solicitada NUMERIC(10,2) NOT NULL,
  cantidad_recibida NUMERIC(10,2) NOT NULL DEFAULT 0.00,
  valor_unitario NUMERIC(15,2) NOT NULL,
  subtotal NUMERIC(15,2) NOT NULL DEFAULT 0.00,
  estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT chk_items_cant_solic CHECK (cantidad_solicitada > 0),
  CONSTRAINT chk_items_cant_recib CHECK (cantidad_recibida >= 0),
  CONSTRAINT chk_items_valor_unit CHECK (valor_unitario > 0),
  CONSTRAINT chk_items_estado CHECK (estado IN ('pendiente','recibido_parcial','recibido'))
);

CREATE INDEX IF NOT EXISTS ix_ped_items_id ON ped_items (id);
CREATE INDEX IF NOT EXISTS ix_ped_items_pedido_id ON ped_items (pedido_id);
CREATE INDEX IF NOT EXISTS ix_ped_items_activo_id ON ped_items (activo_id);
CREATE INDEX IF NOT EXISTS ix_ped_items_estado ON ped_items (estado);

CREATE TABLE IF NOT EXISTS ped_historial_estados (
  id SERIAL PRIMARY KEY,
  pedido_id INTEGER NOT NULL REFERENCES ped_pedidos(id) ON DELETE CASCADE,
  estado_anterior VARCHAR(20) NULL,
  estado_nuevo VARCHAR(20) NOT NULL,
  usuario_id BIGINT NOT NULL,
  fecha_cambio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  comentario TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ped_historial_estados_id ON ped_historial_estados (id);
CREATE INDEX IF NOT EXISTS ix_ped_historial_estados_pedido_id ON ped_historial_estados (pedido_id);
CREATE INDEX IF NOT EXISTS ix_ped_historial_estados_usuario_id ON ped_historial_estados (usuario_id);
CREATE INDEX IF NOT EXISTS ix_ped_historial_estados_fecha_cambio ON ped_historial_estados (fecha_cambio);
