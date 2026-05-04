from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Reserva(Base):
    __tablename__ = "res_reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    espacio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(180), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    cancelled_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class PoliticaReserva(Base):
    __tablename__ = "res_politicas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    min_anticipacion_horas: Mapped[int] = mapped_column(Integer, nullable=False)
    max_anticipacion_dias: Mapped[int] = mapped_column(Integer, nullable=False)
    duracion_max_horas: Mapped[int] = mapped_column(Integer, nullable=False)
    limite_cancelacion_horas: Mapped[int] = mapped_column(Integer, nullable=False)
    max_reservas_activas_usuario: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)


class BloqueoEspacio(Base):
    __tablename__ = "res_bloqueos_espacio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    espacio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
