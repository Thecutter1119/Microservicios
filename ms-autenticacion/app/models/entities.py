from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Sesion(Base):
    __tablename__ = "auth_sesiones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    token_jwt: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(80), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    last_activity_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class TokenAplicacion(Base):
    __tablename__ = "auth_tokens_aplicacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service_name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)


class HistorialAcceso(Base):
    __tablename__ = "auth_historial_accesos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    tipo_evento: Mapped[str] = mapped_column(String(40), nullable=False)
    ip: Mapped[str | None] = mapped_column(String(80), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    event_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())


class IntentoLogin(Base):
    __tablename__ = "auth_intentos_login"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    login_key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    intentos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bloqueado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
