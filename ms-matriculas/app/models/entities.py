from datetime import date, datetime
from sqlalchemy import DATE, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Periodo(Base):
    __tablename__ = "mat_periodos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(DATE, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(DATE, nullable=False)
    fecha_inicio_inscripciones: Mapped[date] = mapped_column(DATE, nullable=False)
    fecha_fin_inscripciones: Mapped[date] = mapped_column(DATE, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default="planificado", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Matricula(Base):
    __tablename__ = "mat_matriculas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    periodo_id: Mapped[int] = mapped_column(ForeignKey("mat_periodos.id"), nullable=False, index=True)
    programa_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
    fecha_matricula: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    semestre_actual: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Inscripcion(Base):
    __tablename__ = "mat_inscripciones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    matricula_id: Mapped[int] = mapped_column(ForeignKey("mat_matriculas.id"), nullable=False, index=True)
    asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    franja_horaria_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="inscrita", nullable=False)
    fecha_inscripcion: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    cancelada_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
