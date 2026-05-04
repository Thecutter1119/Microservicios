from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TipoEspacio(Base):
    __tablename__ = "esp_tipos_espacio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    requiere_equipamiento_especial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())


class Espacio(Base):
    __tablename__ = "esp_espacios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(140), nullable=False)
    tipo_espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_tipos_espacio.id"), nullable=False)
    edificio: Mapped[str] = mapped_column(String(80), nullable=False)
    piso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capacidad_maxima: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default="disponible", nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class EquipamientoEspacio(Base):
    __tablename__ = "esp_equipamiento_espacios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_espacios.id"), nullable=False, index=True)
    activo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    fecha_asignacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())


class Mantenimiento(Base):
    __tablename__ = "esp_mantenimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_espacios.id"), nullable=False, index=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    responsable_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    costo_estimado: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    fecha_programada: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    fecha_ejecucion_real: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="programado", nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class HistorialOcupacion(Base):
    __tablename__ = "esp_historial_ocupacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_espacios.id"), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    horas_ocupadas: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    horas_disponibles: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    porcentaje_uso: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    periodo: Mapped[str] = mapped_column(String(40), nullable=False)
