from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FranjaHoraria(Base):
    __tablename__ = "hor_franjas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    docente_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    espacio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    periodo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    dia_semana: Mapped[str] = mapped_column(String(20), nullable=False)
    hora_inicio: Mapped[str] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[str] = mapped_column(Time, nullable=False)
    grupo: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class AsignacionDocente(Base):
    __tablename__ = "hor_asignaciones_docente"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    docente_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    periodo: Mapped[str] = mapped_column(String(40), nullable=False)
    grupo: Mapped[str] = mapped_column(String(20), nullable=False)
    horas_semanales: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
