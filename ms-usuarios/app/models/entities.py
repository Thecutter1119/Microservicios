from sqlalchemy import DATE, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Usuario(Base):
    __tablename__ = "usr_usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    rol_principal_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Perfil(Base):
    __tablename__ = "usr_perfiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usr_usuarios.id"), unique=True, index=True)
    tipo_documento: Mapped[str | None] = mapped_column(String(20), nullable=True)
    numero_documento: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True, index=True)
    primer_nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    segundo_nombre: Mapped[str | None] = mapped_column(String(80), nullable=True)
    primer_apellido: Mapped[str] = mapped_column(String(80), nullable=False)
    segundo_apellido: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fecha_nacimiento: Mapped[DATE | None] = mapped_column(DATE, nullable=True)
    genero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(180), nullable=True)
    ciudad: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    departamento: Mapped[str | None] = mapped_column(String(80), nullable=True)
    telefono_fijo: Mapped[str | None] = mapped_column(String(30), nullable=True)
    telefono_movil: Mapped[str | None] = mapped_column(String(30), nullable=True)
    contacto_emergencia: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telefono_emergencia: Mapped[str | None] = mapped_column(String(30), nullable=True)
    biografia: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class HistorialEstado(Base):
    __tablename__ = "usr_historial_estados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usr_usuarios.id"), index=True)
    estado_anterior: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String(20), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    changed_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    changed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
