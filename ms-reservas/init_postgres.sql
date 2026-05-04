CREATE DATABASE db_reservas;
\c db_reservas

CREATE TABLE IF NOT EXISTS res_reservas (
    id SERIAL PRIMARY KEY,
    espacio_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    titulo VARCHAR(180) NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    cancelled_by INTEGER,
    motivo_cancelacion TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS res_politicas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    min_anticipacion_horas INTEGER NOT NULL,
    max_anticipacion_dias INTEGER NOT NULL,
    duracion_max_horas INTEGER NOT NULL,
    limite_cancelacion_horas INTEGER NOT NULL,
    max_reservas_activas_usuario INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo'
);

CREATE TABLE IF NOT EXISTS res_bloqueos_espacio (
    id SERIAL PRIMARY KEY,
    espacio_id INTEGER NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    motivo TEXT NOT NULL,
    created_by INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
