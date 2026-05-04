CREATE DATABASE db_horarios;
\c db_horarios

CREATE TABLE IF NOT EXISTS hor_franjas (
    id SERIAL PRIMARY KEY,
    asignatura_id INTEGER NOT NULL,
    docente_id INTEGER NOT NULL,
    espacio_id INTEGER NOT NULL,
    periodo VARCHAR(40) NOT NULL,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    grupo VARCHAR(20) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hor_asignaciones_docente (
    id SERIAL PRIMARY KEY,
    docente_id INTEGER NOT NULL,
    asignatura_id INTEGER NOT NULL,
    periodo VARCHAR(40) NOT NULL,
    grupo VARCHAR(20) NOT NULL,
    horas_semanales INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
