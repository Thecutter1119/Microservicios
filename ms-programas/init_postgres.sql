CREATE DATABASE db_programas;
\c db_programas

CREATE TABLE IF NOT EXISTS prg_programas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(40) NOT NULL UNIQUE,
    nombre VARCHAR(160) NOT NULL,
    descripcion TEXT,
    duracion_semestres INTEGER NOT NULL,
    total_creditos_requeridos INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    coordinador_usuario_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prg_asignaturas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(40) NOT NULL UNIQUE,
    nombre VARCHAR(160) NOT NULL,
    descripcion TEXT,
    creditos INTEGER NOT NULL,
    semestre_sugerido INTEGER NOT NULL,
    programa_id INTEGER NOT NULL REFERENCES prg_programas(id),
    horas_semanales INTEGER NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prg_prerrequisitos (
    id SERIAL PRIMARY KEY,
    asignatura_id INTEGER NOT NULL REFERENCES prg_asignaturas(id),
    prerrequisito_id INTEGER NOT NULL REFERENCES prg_asignaturas(id),
    tipo VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS prg_mallas_version (
    id SERIAL PRIMARY KEY,
    programa_id INTEGER NOT NULL REFERENCES prg_programas(id),
    version_identificador VARCHAR(40) NOT NULL,
    fecha_vigencia_inicio DATE NOT NULL,
    fecha_vigencia_fin DATE,
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    descripcion_cambios TEXT,
    creado_por INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
