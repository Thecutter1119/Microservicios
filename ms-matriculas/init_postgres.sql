CREATE DATABASE db_matriculas;
\c db_matriculas

CREATE TABLE IF NOT EXISTS mat_periodos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(40) NOT NULL UNIQUE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    fecha_inicio_inscripciones DATE NOT NULL,
    fecha_fin_inscripciones DATE NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'planificado',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_matriculas (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL,
    periodo_id INTEGER NOT NULL REFERENCES mat_periodos(id),
    programa_id INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    fecha_matricula TIMESTAMP NOT NULL DEFAULT NOW(),
    semestre_actual INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mat_inscripciones (
    id SERIAL PRIMARY KEY,
    matricula_id INTEGER NOT NULL REFERENCES mat_matriculas(id),
    asignatura_id INTEGER NOT NULL,
    franja_horaria_id INTEGER,
    estado VARCHAR(20) NOT NULL DEFAULT 'inscrita',
    fecha_inscripcion TIMESTAMP NOT NULL DEFAULT NOW(),
    cancelada_por INTEGER,
    motivo_cancelacion TEXT
);
