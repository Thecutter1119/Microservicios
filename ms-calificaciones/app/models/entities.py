from datetime import datetime
from sqlalchemy import DATE, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CorteEvaluativo(Base):
    __tablename__ = "cal_cortes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    periodo_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    numero_corte: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_inicio: Mapped[str] = mapped_column(DATE, nullable=False)
    fecha_fin: Mapped[str] = mapped_column(DATE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())


class Nota(Base):
    __tablename__ = "cal_notas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inscripcion_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    corte_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    nota: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class PromedioEstudiante(Base):
    __tablename__ = "cal_promedios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    estudiante_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    periodo_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    promedio_periodo: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    promedio_acumulado: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    creditos_aprobados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    creditos_cursados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
