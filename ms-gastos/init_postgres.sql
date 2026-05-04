CREATE DATABASE db_gastos;
\c db_gastos

CREATE TABLE IF NOT EXISTS gas_categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    descripcion TEXT,
    requiere_aprobacion_especial BOOLEAN NOT NULL DEFAULT FALSE,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo'
);

CREATE TABLE IF NOT EXISTS gas_gastos (
    id SERIAL PRIMARY KEY,
    descripcion TEXT NOT NULL,
    monto NUMERIC(14,2) NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES gas_categorias(id),
    partida_presupuestal_id INTEGER NOT NULL,
    proveedor_id INTEGER,
    estado VARCHAR(20) NOT NULL DEFAULT 'solicitado',
    solicitado_por INTEGER,
    fecha_solicitud TIMESTAMP NOT NULL DEFAULT NOW(),
    aprobado_por INTEGER,
    fecha_aprobacion TIMESTAMP,
    fecha_pago TIMESTAMP,
    observaciones TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gas_novedades (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER NOT NULL REFERENCES gas_gastos(id),
    tipo_novedad VARCHAR(40) NOT NULL,
    descripcion TEXT NOT NULL,
    monto_impacto NUMERIC(14,2) NOT NULL,
    reportado_por INTEGER,
    fecha_reporte TIMESTAMP NOT NULL DEFAULT NOW(),
    estado VARCHAR(20) NOT NULL DEFAULT 'abierta'
);

CREATE TABLE IF NOT EXISTS gas_aprobaciones (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER NOT NULL REFERENCES gas_gastos(id),
    aprobador_id INTEGER,
    decision VARCHAR(20) NOT NULL,
    comentario TEXT,
    fecha TIMESTAMP NOT NULL DEFAULT NOW()
);
