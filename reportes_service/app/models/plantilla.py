"""
ms-reportes [REP] — Modelo ORM: rep_plantillas
Entidad principal — catálogo de plantillas de reporte
REP-RF-006 a REP-RF-010
"""

from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Plantilla(Base):
    __tablename__ = "rep_plantillas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    microservicios_fuente: Mapped[dict] = mapped_column(JSONB, nullable=False)
    parametros_requeridos: Mapped[dict] = mapped_column(JSONB, nullable=False)
    configuracion_consultas: Mapped[dict] = mapped_column(JSONB, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="activa",
        comment="activa | inactiva"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relaciones
    reportes: Mapped[list["Reporte"]] = relationship("Reporte", back_populates="plantilla", lazy="select")
    programaciones: Mapped[list["Programacion"]] = relationship("Programacion", back_populates="plantilla", lazy="select")
