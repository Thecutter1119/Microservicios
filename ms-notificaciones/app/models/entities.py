from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Notificacion(Base):
    __tablename__ = "not_notificaciones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    canal: Mapped[str] = mapped_column(String(20), nullable=False)
    asunto: Mapped[str | None] = mapped_column(String(180), nullable=True)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    prioridad: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    intentos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_intentos: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    fecha_lectura: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Plantilla(Base):
    __tablename__ = "not_plantillas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    canal: Mapped[str] = mapped_column(String(20), nullable=False)
    asunto_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    mensaje_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables_requeridas: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class PreferenciaUsuario(Base):
    __tablename__ = "not_preferencias_usuario"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    canal_preferido: Mapped[str] = mapped_column(String(20), nullable=False)
    notificaciones_activas: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    no_molestar_inicio: Mapped[str | None] = mapped_column(Time, nullable=True)
    no_molestar_fin: Mapped[str | None] = mapped_column(Time, nullable=True)


class HistorialReintento(Base):
    __tablename__ = "not_historial_reintentos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    notificacion_id: Mapped[int] = mapped_column(ForeignKey("not_notificaciones.id"), nullable=False, index=True)
    numero_intento: Mapped[int] = mapped_column(Integer, nullable=False)
    resultado: Mapped[str] = mapped_column(String(20), nullable=False)
    detalle_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
