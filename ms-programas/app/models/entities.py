from datetime import date, datetime
from sqlalchemy import DATE, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Programa(Base):
    __tablename__ = "prg_programas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    duracion_semestres: Mapped[int] = mapped_column(Integer, nullable=False)
    total_creditos_requeridos: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    coordinador_usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Asignatura(Base):
    __tablename__ = "prg_asignaturas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    creditos: Mapped[int] = mapped_column(Integer, nullable=False)
    semestre_sugerido: Mapped[int] = mapped_column(Integer, nullable=False)
    programa_id: Mapped[int] = mapped_column(ForeignKey("prg_programas.id"), nullable=False, index=True)
    horas_semanales: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Prerrequisito(Base):
    __tablename__ = "prg_prerrequisitos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asignatura_id: Mapped[int] = mapped_column(ForeignKey("prg_asignaturas.id"), nullable=False, index=True)
    prerrequisito_id: Mapped[int] = mapped_column(ForeignKey("prg_asignaturas.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)


class MallaVersion(Base):
    __tablename__ = "prg_mallas_version"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    programa_id: Mapped[int] = mapped_column(ForeignKey("prg_programas.id"), nullable=False, index=True)
    version_identificador: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha_vigencia_inicio: Mapped[date] = mapped_column(DATE, nullable=False)
    fecha_vigencia_fin: Mapped[date | None] = mapped_column(DATE, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="borrador", nullable=False)
    descripcion_cambios: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
