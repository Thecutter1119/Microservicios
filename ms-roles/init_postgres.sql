CREATE DATABASE db_roles;
\c db_roles

CREATE TABLE IF NOT EXISTS rol_roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rol_permisos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(80) NOT NULL UNIQUE,
    nombre VARCHAR(120) NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(80) NOT NULL,
    microservicio_origen VARCHAR(80) NOT NULL,
    funcionalidad VARCHAR(120) NOT NULL,
    metodo_operacion VARCHAR(40) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rol_asignaciones_rol_permiso (
    id SERIAL PRIMARY KEY,
    rol_id INTEGER NOT NULL REFERENCES rol_roles(id),
    permiso_id INTEGER NOT NULL REFERENCES rol_permisos(id),
    assigned_by INTEGER,
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (rol_id, permiso_id)
);

CREATE TABLE IF NOT EXISTS rol_asignaciones_usuario_rol (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    rol_id INTEGER NOT NULL REFERENCES rol_roles(id),
    assigned_by INTEGER,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (usuario_id, rol_id)
);
