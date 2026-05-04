CREATE DATABASE db_notificaciones;
\c db_notificaciones

CREATE TABLE IF NOT EXISTS not_notificaciones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    canal VARCHAR(20) NOT NULL,
    asunto VARCHAR(180),
    mensaje TEXT NOT NULL,
    prioridad VARCHAR(20) NOT NULL DEFAULT 'normal',
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    intentos INTEGER NOT NULL DEFAULT 0,
    max_intentos INTEGER NOT NULL DEFAULT 3,
    request_id VARCHAR(80),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_envio TIMESTAMP,
    fecha_lectura TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS not_plantillas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    canal VARCHAR(20) NOT NULL,
    asunto_template TEXT,
    mensaje_template TEXT NOT NULL,
    variables_requeridas TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS not_preferencias_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE,
    canal_preferido VARCHAR(20) NOT NULL,
    notificaciones_activas BOOLEAN NOT NULL DEFAULT TRUE,
    no_molestar_inicio TIME,
    no_molestar_fin TIME
);

CREATE TABLE IF NOT EXISTS not_historial_reintentos (
    id SERIAL PRIMARY KEY,
    notificacion_id INTEGER NOT NULL REFERENCES not_notificaciones(id),
    numero_intento INTEGER NOT NULL,
    resultado VARCHAR(20) NOT NULL,
    detalle_error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
