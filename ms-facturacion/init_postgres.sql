CREATE DATABASE db_facturacion;
\c db_facturacion

CREATE TABLE IF NOT EXISTS fac_conceptos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(140) NOT NULL UNIQUE,
    descripcion TEXT,
    valor_base NUMERIC(14,2) NOT NULL,
    es_recurrente BOOLEAN NOT NULL DEFAULT FALSE,
    periodicidad VARCHAR(40),
    estado VARCHAR(20) NOT NULL DEFAULT 'activo'
);

CREATE TABLE IF NOT EXISTS fac_facturas (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(40) NOT NULL UNIQUE,
    usuario_id INTEGER NOT NULL,
    fecha_emision TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_vencimiento TIMESTAMP NOT NULL,
    subtotal NUMERIC(14,2) NOT NULL DEFAULT 0,
    porcentaje_impuesto NUMERIC(6,2) NOT NULL DEFAULT 0,
    valor_impuesto NUMERIC(14,2) NOT NULL DEFAULT 0,
    total NUMERIC(14,2) NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'emitida',
    fecha_pago TIMESTAMP,
    observaciones TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fac_detalles_factura (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES fac_facturas(id),
    concepto_id INTEGER NOT NULL REFERENCES fac_conceptos(id),
    descripcion TEXT,
    cantidad INTEGER NOT NULL,
    valor_unitario NUMERIC(14,2) NOT NULL,
    subtotal_linea NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS fac_estados_cuenta (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE,
    total_facturado NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_pagado NUMERIC(14,2) NOT NULL DEFAULT 0,
    saldo_pendiente NUMERIC(14,2) NOT NULL DEFAULT 0,
    facturas_vencidas INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
