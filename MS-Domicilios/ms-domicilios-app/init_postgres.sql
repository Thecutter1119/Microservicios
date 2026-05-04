-- ms-domicilios (DOM) - Inicialización PostgreSQL (psql)
-- Crea la base de datos y las tablas requeridas.

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', 'domicilios', 'domicilios123')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'domicilios')\gexec

SELECT format('CREATE DATABASE %I OWNER %I', 'ms_domicilios', 'domicilios')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ms_domicilios')\gexec

ALTER DATABASE ms_domicilios OWNER TO domicilios;
GRANT ALL PRIVILEGES ON DATABASE ms_domicilios TO domicilios;

\connect ms_domicilios

GRANT CREATE ON SCHEMA public TO domicilios;
SET ROLE domicilios;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'entrega_estado') THEN
    CREATE TYPE entrega_estado AS ENUM ('pendiente','asignada','en_camino','entregada','fallida','devuelta');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'repartidor_estado') THEN
    CREATE TYPE repartidor_estado AS ENUM ('disponible','en_ruta','inactivo');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'seguimiento_tipo') THEN
    CREATE TYPE seguimiento_tipo AS ENUM ('manual','automatico');
  END IF;
END
$$;

CREATE TABLE IF NOT EXISTS repartidores (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER NOT NULL,
  nombre VARCHAR(120) NOT NULL,
  telefono VARCHAR(30) NOT NULL,
  tipo_vehiculo VARCHAR(50) NOT NULL,
  placa_vehiculo VARCHAR(20) NOT NULL,
  zona_cobertura VARCHAR(120) NOT NULL,
  estado repartidor_estado NOT NULL DEFAULT 'disponible',
  calificacion_promedio DOUBLE PRECISION NULL,
  fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_repartidores_placa_vehiculo UNIQUE (placa_vehiculo)
);

CREATE INDEX IF NOT EXISTS ix_repartidores_id ON repartidores (id);
CREATE INDEX IF NOT EXISTS ix_repartidores_usuario_id ON repartidores (usuario_id);
CREATE INDEX IF NOT EXISTS ix_repartidores_placa_vehiculo ON repartidores (placa_vehiculo);
CREATE INDEX IF NOT EXISTS ix_repartidores_zona_cobertura ON repartidores (zona_cobertura);

CREATE TABLE IF NOT EXISTS entregas (
  id SERIAL PRIMARY KEY,
  pedido_id INTEGER NOT NULL,
  repartidor_id INTEGER NULL REFERENCES repartidores(id),
  origen VARCHAR(255) NOT NULL,
  destino VARCHAR(255) NOT NULL,
  observaciones TEXT NULL,
  estado entrega_estado NOT NULL DEFAULT 'pendiente',
  costo_envio DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_entregas_pedido_id UNIQUE (pedido_id)
);

CREATE INDEX IF NOT EXISTS ix_entregas_id ON entregas (id);
CREATE INDEX IF NOT EXISTS ix_entregas_pedido_id ON entregas (pedido_id);
CREATE INDEX IF NOT EXISTS ix_entregas_estado_fecha ON entregas (estado, fecha_creacion);

CREATE TABLE IF NOT EXISTS seguimientos (
  id SERIAL PRIMARY KEY,
  entrega_id INTEGER NOT NULL REFERENCES entregas(id) ON DELETE CASCADE,
  tipo seguimiento_tipo NOT NULL DEFAULT 'manual',
  latitud NUMERIC(9,6) NOT NULL,
  longitud NUMERIC(9,6) NOT NULL,
  descripcion VARCHAR(255) NULL,
  fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_seguimientos_id ON seguimientos (id);
CREATE INDEX IF NOT EXISTS ix_seguimientos_entrega_id ON seguimientos (entrega_id);
CREATE INDEX IF NOT EXISTS ix_seguimientos_entrega_fecha ON seguimientos (entrega_id, fecha_registro);

CREATE TABLE IF NOT EXISTS calificaciones (
  id SERIAL PRIMARY KEY,
  entrega_id INTEGER NOT NULL REFERENCES entregas(id) ON DELETE CASCADE,
  repartidor_id INTEGER NOT NULL REFERENCES repartidores(id),
  solicitante_id INTEGER NOT NULL,
  puntaje INTEGER NOT NULL,
  comentario TEXT NULL,
  fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_calificaciones_entrega_id UNIQUE (entrega_id)
);

CREATE INDEX IF NOT EXISTS ix_calificaciones_id ON calificaciones (id);
CREATE INDEX IF NOT EXISTS ix_calificaciones_entrega_id ON calificaciones (entrega_id);
CREATE INDEX IF NOT EXISTS ix_calificaciones_repartidor_id ON calificaciones (repartidor_id);
CREATE INDEX IF NOT EXISTS ix_calificaciones_solicitante_id ON calificaciones (solicitante_id);
