from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CategoriaGasto(Base):
    __tablename__ = "gas_categorias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    requiere_aprobacion_especial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)


class Gasto(Base):
    __tablename__ = "gas_gastos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("gas_categorias.id"), nullable=False)
    partida_presupuestal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    proveedor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="solicitado", nullable=False)
    solicitado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    aprobado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    fecha_pago: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Novedad(Base):
    __tablename__ = "gas_novedades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gasto_id: Mapped[int] = mapped_column(ForeignKey("gas_gastos.id"), nullable=False, index=True)
    tipo_novedad: Mapped[str] = mapped_column(String(40), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    monto_impacto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    reportado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_reporte: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    estado: Mapped[str] = mapped_column(String(20), default="abierta", nullable=False)


class Aprobacion(Base):
    __tablename__ = "gas_aprobaciones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gasto_id: Mapped[int] = mapped_column(ForeignKey("gas_gastos.id"), nullable=False, index=True)
    aprobador_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
