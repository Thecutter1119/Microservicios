CREATE DATABASE db_auditoria;
\c db_auditoria

CREATE TABLE IF NOT EXISTS aud_eventos (
    id SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP NOT NULL DEFAULT NOW(),
    request_id VARCHAR(80),
    microservicio VARCHAR(80) NOT NULL,
    funcionalidad VARCHAR(140),
    metodo VARCHAR(20),
    codigo_respuesta INTEGER,
    duracion_ms INTEGER,
    usuario_id INTEGER,
    detalle TEXT
);

CREATE TABLE IF NOT EXISTS aud_retencion (
    id SERIAL PRIMARY KEY,
    dias_retencion INTEGER NOT NULL DEFAULT 30,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    ultima_rotacion TIMESTAMP,
    registros_eliminados_ultima_rotacion INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS aud_estadisticas (
    id SERIAL PRIMARY KEY,
    microservicio VARCHAR(80) NOT NULL,
    periodo VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    total_peticiones INTEGER NOT NULL,
    total_errores INTEGER NOT NULL,
    tiempo_promedio_ms NUMERIC(10,2) NOT NULL,
    funcionalidad_mas_utilizada VARCHAR(140),
    fecha_calculo TIMESTAMP NOT NULL DEFAULT NOW()
);
