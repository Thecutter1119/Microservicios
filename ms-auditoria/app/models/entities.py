from datetime import date, datetime
from sqlalchemy import DATE, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EventoLog(Base):
    __tablename__ = "aud_eventos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    microservicio: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    funcionalidad: Mapped[str | None] = mapped_column(String(140), nullable=True)
    metodo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    codigo_respuesta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duracion_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)


class ConfigRetencion(Base):
    __tablename__ = "aud_retencion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dias_retencion: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
    ultima_rotacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    registros_eliminados_ultima_rotacion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class EstadisticaServicio(Base):
    __tablename__ = "aud_estadisticas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    microservicio: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    periodo: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha: Mapped[date] = mapped_column(DATE, nullable=False)
    total_peticiones: Mapped[int] = mapped_column(Integer, nullable=False)
    total_errores: Mapped[int] = mapped_column(Integer, nullable=False)
    tiempo_promedio_ms: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    funcionalidad_mas_utilizada: Mapped[str | None] = mapped_column(String(140), nullable=True)
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
