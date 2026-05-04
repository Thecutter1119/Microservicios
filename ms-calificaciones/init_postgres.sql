CREATE DATABASE db_calificaciones;
\c db_calificaciones

CREATE TABLE IF NOT EXISTS cal_cortes (
    id SERIAL PRIMARY KEY,
    asignatura_id INTEGER NOT NULL,
    periodo_id INTEGER NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    porcentaje NUMERIC(5,2) NOT NULL,
    numero_corte INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cal_notas (
    id SERIAL PRIMARY KEY,
    inscripcion_id INTEGER NOT NULL,
    corte_id INTEGER NOT NULL REFERENCES cal_cortes(id),
    nota NUMERIC(3,1) NOT NULL,
    observaciones TEXT,
    registrado_por INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cal_promedios (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL,
    periodo_id INTEGER NOT NULL,
    promedio_periodo NUMERIC(4,2) NOT NULL,
    promedio_acumulado NUMERIC(4,2) NOT NULL,
    creditos_aprobados INTEGER NOT NULL DEFAULT 0,
    creditos_cursados INTEGER NOT NULL DEFAULT 0,
    fecha_calculo TIMESTAMP NOT NULL DEFAULT NOW()
);
