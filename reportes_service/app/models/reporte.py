"""
ms-reportes [REP] — Modelo ORM: rep_reportes
Entidad de mayor volumen — cada instancia de reporte generado
REP-RF-011 a REP-RF-014, REP-RF-021, REP-RF-022
"""

from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Reporte(Base):
    __tablename__ = "rep_reportes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plantilla_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rep_plantillas.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    parametros: Mapped[dict] = mapped_column(JSONB, nullable=False)
    resultado_cache: Mapped[str | None] = mapped_column(Text, nullable=True)
    formato_salida: Mapped[str] = mapped_column(String(10), nullable=False, comment="CSV | JSON")
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pendiente",
        comment="pendiente | generando | completado | error"
    )
    # Ref. externa a ms-autenticacion — sin FK real
    solicitado_por: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    fecha_generacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tamano_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    # Relaciones
    plantilla: Mapped["Plantilla"] = relationship("Plantilla", back_populates="reportes")
