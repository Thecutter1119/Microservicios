from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ConceptoCobro(Base):
    __tablename__ = "fac_conceptos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor_base: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    es_recurrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    periodicidad: Mapped[str | None] = mapped_column(String(40), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)


class Factura(Base):
    __tablename__ = "fac_facturas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero_factura: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    porcentaje_impuesto: Mapped[float] = mapped_column(Numeric(6, 2), default=0, nullable=False)
    valor_impuesto: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="emitida", nullable=False)
    fecha_pago: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class FacturaDetalle(Base):
    __tablename__ = "fac_detalles_factura"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("fac_facturas.id"), nullable=False, index=True)
    concepto_id: Mapped[int] = mapped_column(ForeignKey("fac_conceptos.id"), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_unitario: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal_linea: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)


class EstadoCuenta(Base):
    __tablename__ = "fac_estados_cuenta"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    total_facturado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_pagado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    saldo_pendiente: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    facturas_vencidas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
