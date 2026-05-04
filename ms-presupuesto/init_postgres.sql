CREATE DATABASE db_presupuesto;
\c db_presupuesto

CREATE TABLE IF NOT EXISTS pre_presupuestos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(140) NOT NULL,
    periodo VARCHAR(40) NOT NULL,
    monto_total NUMERIC(14,2) NOT NULL,
    monto_ejecutado NUMERIC(14,2) NOT NULL DEFAULT 0,
    monto_disponible NUMERIC(14,2) NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    approved_by INTEGER,
    approved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pre_partidas (
    id SERIAL PRIMARY KEY,
    presupuesto_id INTEGER NOT NULL REFERENCES pre_presupuestos(id),
    nombre VARCHAR(140) NOT NULL,
    area_destino VARCHAR(120) NOT NULL,
    monto_asignado NUMERIC(14,2) NOT NULL,
    monto_ejecutado NUMERIC(14,2) NOT NULL DEFAULT 0,
    monto_disponible NUMERIC(14,2) NOT NULL DEFAULT 0,
    porcentaje_alerta INTEGER NOT NULL DEFAULT 80,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pre_reasignaciones (
    id SERIAL PRIMARY KEY,
    partida_origen_id INTEGER NOT NULL REFERENCES pre_partidas(id),
    partida_destino_id INTEGER NOT NULL REFERENCES pre_partidas(id),
    monto NUMERIC(14,2) NOT NULL,
    motivo TEXT NOT NULL,
    solicitado_por INTEGER,
    aprobado_por INTEGER,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
