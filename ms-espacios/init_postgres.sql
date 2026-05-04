CREATE DATABASE db_espacios;
\c db_espacios

CREATE TABLE IF NOT EXISTS esp_tipos_espacio (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT,
    requiere_equipamiento_especial BOOLEAN NOT NULL DEFAULT FALSE,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS esp_espacios (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(40) NOT NULL UNIQUE,
    nombre VARCHAR(140) NOT NULL,
    tipo_espacio_id INTEGER NOT NULL REFERENCES esp_tipos_espacio(id),
    edificio VARCHAR(80) NOT NULL,
    piso INTEGER,
    capacidad_maxima INTEGER NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'disponible',
    descripcion TEXT,
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS esp_equipamiento_espacios (
    id SERIAL PRIMARY KEY,
    espacio_id INTEGER NOT NULL REFERENCES esp_espacios(id),
    activo_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    fecha_asignacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS esp_mantenimientos (
    id SERIAL PRIMARY KEY,
    espacio_id INTEGER NOT NULL REFERENCES esp_espacios(id),
    descripcion TEXT NOT NULL,
    responsable_id INTEGER,
    costo_estimado NUMERIC(14,2),
    fecha_programada TIMESTAMP NOT NULL,
    fecha_ejecucion_real TIMESTAMP,
    estado VARCHAR(30) NOT NULL DEFAULT 'programado',
    observaciones TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS esp_historial_ocupacion (
    id SERIAL PRIMARY KEY,
    espacio_id INTEGER NOT NULL REFERENCES esp_espacios(id),
    fecha DATE NOT NULL,
    horas_ocupadas NUMERIC(6,2) NOT NULL,
    horas_disponibles NUMERIC(6,2) NOT NULL,
    porcentaje_uso NUMERIC(6,2) NOT NULL,
    periodo VARCHAR(40) NOT NULL
);
