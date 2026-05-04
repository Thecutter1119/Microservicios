CREATE DATABASE db_inventario;
\c db_inventario

CREATE TABLE IF NOT EXISTS inv_categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    descripcion TEXT,
    categoria_padre_id INTEGER REFERENCES inv_categorias(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS inv_activos (
    id SERIAL PRIMARY KEY,
    codigo_interno VARCHAR(60) NOT NULL UNIQUE,
    nombre VARCHAR(180) NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER NOT NULL REFERENCES inv_categorias(id),
    proveedor_id INTEGER,
    precio_adquisicion NUMERIC(14,2) NOT NULL,
    fecha_adquisicion DATE NOT NULL,
    vida_util_meses INTEGER NOT NULL,
    valor_depreciacion_actual NUMERIC(14,2) NOT NULL DEFAULT 0,
    ubicacion_fisica VARCHAR(180),
    estado VARCHAR(30) NOT NULL DEFAULT 'disponible',
    stock_actual INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS inv_movimientos_stock (
    id SERIAL PRIMARY KEY,
    activo_id INTEGER NOT NULL REFERENCES inv_activos(id),
    tipo_movimiento VARCHAR(20) NOT NULL,
    cantidad INTEGER NOT NULL,
    motivo TEXT NOT NULL,
    usuario_responsable_id INTEGER,
    pedido_referencia VARCHAR(80),
    request_id VARCHAR(80),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
