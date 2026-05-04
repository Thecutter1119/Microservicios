from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Rol(Base):
    __tablename__ = "rol_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Permiso(Base):
    __tablename__ = "rol_permisos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    modulo: Mapped[str] = mapped_column(String(80), nullable=False)
    microservicio_origen: Mapped[str] = mapped_column(String(80), nullable=False)
    funcionalidad: Mapped[str] = mapped_column(String(120), nullable=False)
    metodo_operacion: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class RolPermiso(Base):
    __tablename__ = "rol_asignaciones_rol_permiso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("rol_roles.id"), index=True)
    permiso_id: Mapped[int] = mapped_column(ForeignKey("rol_permisos.id"), index=True)
    assigned_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assigned_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())


class UsuarioRol(Base):
    __tablename__ = "rol_asignaciones_usuario_rol"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, index=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("rol_roles.id"), index=True)
    assigned_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
    assigned_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
