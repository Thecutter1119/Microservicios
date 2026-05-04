from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Presupuesto(Base):
    __tablename__ = "pre_presupuestos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(140), nullable=False)
    periodo: Mapped[str] = mapped_column(String(40), nullable=False)
    monto_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    monto_ejecutado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    monto_disponible: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="borrador", nullable=False)
    approved_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Partida(Base):
    __tablename__ = "pre_partidas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    presupuesto_id: Mapped[int] = mapped_column(ForeignKey("pre_presupuestos.id"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(140), nullable=False)
    area_destino: Mapped[str] = mapped_column(String(120), nullable=False)
    monto_asignado: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    monto_ejecutado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    monto_disponible: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    porcentaje_alerta: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Reasignacion(Base):
    __tablename__ = "pre_reasignaciones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    partida_origen_id: Mapped[int] = mapped_column(ForeignKey("pre_partidas.id"), nullable=False)
    partida_destino_id: Mapped[int] = mapped_column(ForeignKey("pre_partidas.id"), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    solicitado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aprobado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
