CREATE DATABASE db_autenticacion;
\c db_autenticacion

CREATE TABLE IF NOT EXISTS auth_sesiones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    token_jwt TEXT NOT NULL UNIQUE,
    ip VARCHAR(80),
    user_agent VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth_tokens_aplicacion (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(80) NOT NULL UNIQUE,
    token_encrypted TEXT NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_by INTEGER
);

CREATE TABLE IF NOT EXISTS auth_historial_accesos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    tipo_evento VARCHAR(40) NOT NULL,
    ip VARCHAR(80),
    user_agent VARCHAR(255),
    request_id VARCHAR(80),
    event_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth_intentos_login (
    id SERIAL PRIMARY KEY,
    login_key VARCHAR(120) NOT NULL UNIQUE,
    intentos INTEGER NOT NULL DEFAULT 0,
    bloqueado BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
