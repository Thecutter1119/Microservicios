CREATE DATABASE db_usuarios;
\c db_usuarios

CREATE TABLE IF NOT EXISTS usr_usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    rol_principal_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS usr_perfiles (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE REFERENCES usr_usuarios(id),
    tipo_documento VARCHAR(20),
    numero_documento VARCHAR(40) UNIQUE,
    primer_nombre VARCHAR(80) NOT NULL,
    segundo_nombre VARCHAR(80),
    primer_apellido VARCHAR(80) NOT NULL,
    segundo_apellido VARCHAR(80),
    fecha_nacimiento DATE,
    genero VARCHAR(20),
    direccion VARCHAR(180),
    ciudad VARCHAR(80),
    departamento VARCHAR(80),
    telefono_fijo VARCHAR(30),
    telefono_movil VARCHAR(30),
    contacto_emergencia VARCHAR(120),
    telefono_emergencia VARCHAR(30),
    biografia TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS usr_historial_estados (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usr_usuarios(id),
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20) NOT NULL,
    motivo TEXT NOT NULL,
    changed_by INTEGER,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW()
);
