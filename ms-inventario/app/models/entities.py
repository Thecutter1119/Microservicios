from datetime import date
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Categoria(Base):
    __tablename__ = "inv_categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria_padre_id: Mapped[int | None] = mapped_column(ForeignKey("inv_categorias.id"), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())


class Activo(Base):
    __tablename__ = "inv_activos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo_interno: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(180), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("inv_categorias.id"), nullable=False)
    proveedor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    precio_adquisicion: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    fecha_adquisicion: Mapped[date] = mapped_column(Date, nullable=False)
    vida_util_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_depreciacion_actual: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    ubicacion_fisica: Mapped[str | None] = mapped_column(String(180), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="disponible", nullable=False)
    stock_actual: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class MovimientoStock(Base):
    __tablename__ = "inv_movimientos_stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    activo_id: Mapped[int] = mapped_column(ForeignKey("inv_activos.id"), nullable=False, index=True)
    tipo_movimiento: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    usuario_responsable_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pedido_referencia: Mapped[str | None] = mapped_column(String(80), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
