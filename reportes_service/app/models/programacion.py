"""
ms-reportes [REP] — Modelo ORM: rep_programaciones
Entidad de automatización — ciclo de ejecución periódica
REP-RF-015 a REP-RF-020, REP-RF-023, REP-RF-024
"""

from datetime import datetime, time
from sqlalchemy import BigInteger, String, DateTime, Time, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Programacion(Base):
    __tablename__ = "rep_programaciones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plantilla_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rep_plantillas.id"), nullable=False)
    periodicidad: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="diario | semanal | mensual"
    )
    dia_ejecucion: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="NULL para diario; nombre del día (semanal); número del día (mensual)"
    )
    hora_ejecucion: Mapped[time] = mapped_column(Time, nullable=False)
    # Ref. externa a ms-autenticacion/ms-roles — sin FK real
    destinatarios: Mapped[dict] = mapped_column(JSONB, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="activa",
        comment="activa | pausada"
    )
    ultima_ejecucion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    proxima_ejecucion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relaciones
    plantilla: Mapped["Plantilla"] = relationship("Plantilla", back_populates="programaciones")
