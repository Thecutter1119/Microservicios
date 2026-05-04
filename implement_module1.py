from pathlib import Path
from textwrap import dedent

ROOT = Path(r"c:\Users\jhons\Downloads\Microservicios")


def write(rel_path: str, content: str) -> None:
    file_path = ROOT / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


write(
    "ms-roles/requirements.txt",
    dedent(
        """\
        fastapi==0.115.0
        uvicorn==0.30.6
        sqlalchemy==2.0.36
        psycopg[binary]==3.2.3
        pydantic==2.9.2
        pydantic-settings==2.6.0
        """
    ),
)

write(
    "ms-roles/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-roles
        SERVICE_CODE=ROL
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_roles
        CONTRADICTORY_ROLE_PAIRS=DOCENTE:ESTUDIANTE
        """
    ),
)

write(
    "ms-roles/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_roles;
        \\c db_roles

        CREATE TABLE IF NOT EXISTS rol_roles (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(80) NOT NULL UNIQUE,
            descripcion TEXT,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS rol_permisos (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(80) NOT NULL UNIQUE,
            nombre VARCHAR(120) NOT NULL,
            descripcion TEXT,
            modulo VARCHAR(80) NOT NULL,
            microservicio_origen VARCHAR(80) NOT NULL,
            funcionalidad VARCHAR(120) NOT NULL,
            metodo_operacion VARCHAR(40) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS rol_asignaciones_rol_permiso (
            id SERIAL PRIMARY KEY,
            rol_id INTEGER NOT NULL REFERENCES rol_roles(id),
            permiso_id INTEGER NOT NULL REFERENCES rol_permisos(id),
            assigned_by INTEGER,
            assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE (rol_id, permiso_id)
        );

        CREATE TABLE IF NOT EXISTS rol_asignaciones_usuario_rol (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            rol_id INTEGER NOT NULL REFERENCES rol_roles(id),
            assigned_by INTEGER,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE (usuario_id, rol_id)
        );
        """
    ),
)

write(
    "ms-roles/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-roles"
            SERVICE_CODE: str = "ROL"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_roles"
            CONTRADICTORY_ROLE_PAIRS: str = "DOCENTE:ESTUDIANTE"
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)

write(
    "ms-roles/app/models/entities.py",
    dedent(
        """\
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
        """
    ),
)

write(
    "ms-roles/app/schemas/entities.py",
    dedent(
        """\
        from datetime import datetime
        from pydantic import BaseModel, ConfigDict


        class RolIn(BaseModel):
            nombre: str
            descripcion: str | None = None


        class RolOut(BaseModel):
            id: int
            nombre: str
            descripcion: str | None = None
            estado: str
            created_at: datetime | None = None
            updated_at: datetime | None = None
            model_config = ConfigDict(from_attributes=True)


        class PermisoIn(BaseModel):
            codigo: str
            nombre: str
            descripcion: str | None = None
            modulo: str
            microservicio_origen: str
            funcionalidad: str
            metodo_operacion: str


        class PermisoOut(PermisoIn):
            id: int
            created_at: datetime | None = None
            updated_at: datetime | None = None
            model_config = ConfigDict(from_attributes=True)


        class AssignPermisosIn(BaseModel):
            permiso_ids: list[int]
            assigned_by: int | None = None


        class AssignRolUsuarioIn(BaseModel):
            rol_id: int
            assigned_by: int | None = None


        class RemoveRolUsuarioIn(BaseModel):
            rol_id: int
        """
    ),
)

write(
    "ms-roles/app/db/init_db.py",
    dedent(
        """\
        from app.db.session import Base, SessionLocal, engine
        from app.models.entities import Permiso, Rol, RolPermiso, UsuarioRol  # noqa: F401


        BASIC_ROLES = ["Administrador", "Docente", "Estudiante", "Operador"]
        BASIC_PERMISSIONS = [
            {
                "codigo": "AUTH_VALIDATE_SESSION",
                "nombre": "Validar sesion",
                "descripcion": "Permite validar sesiones de usuario",
                "modulo": "Seguridad",
                "microservicio_origen": "ms-autenticacion",
                "funcionalidad": "Validacion de sesion",
                "metodo_operacion": "consulta",
            },
            {
                "codigo": "ROL_VALIDATE_PERMISSION",
                "nombre": "Validar permiso",
                "descripcion": "Permite validar permisos por rol",
                "modulo": "Seguridad",
                "microservicio_origen": "ms-roles",
                "funcionalidad": "Validacion de permiso",
                "metodo_operacion": "consulta",
            },
            {
                "codigo": "USR_CREATE",
                "nombre": "Crear usuario",
                "descripcion": "Permite crear usuarios",
                "modulo": "Seguridad",
                "microservicio_origen": "ms-usuarios",
                "funcionalidad": "Creacion de usuario",
                "metodo_operacion": "creacion",
            },
        ]


        def init_db() -> None:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                for role_name in BASIC_ROLES:
                    if not db.query(Rol).filter(Rol.nombre == role_name).first():
                        db.add(Rol(nombre=role_name, descripcion=f"Rol base: {role_name}"))
                db.commit()
                for perm in BASIC_PERMISSIONS:
                    if not db.query(Permiso).filter(Permiso.codigo == perm["codigo"]).first():
                        db.add(Permiso(**perm))
                db.commit()
            finally:
                db.close()
        """
    ),
)

write(
    "ms-roles/app/api/routes/entities.py",
    dedent(
        """\
        from collections import defaultdict

        from fastapi import APIRouter, Depends, HTTPException, Query
        from sqlalchemy import and_
        from sqlalchemy.orm import Session

        from app.core.config import settings
        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import Permiso, Rol, RolPermiso, UsuarioRol
        from app.schemas.entities import AssignPermisosIn, AssignRolUsuarioIn, PermisoIn, PermisoOut, RemoveRolUsuarioIn, RolIn, RolOut

        router = APIRouter(tags=["ms-roles"])


        def _contradictory_pairs() -> set[tuple[str, str]]:
            pairs = set()
            for raw in settings.CONTRADICTORY_ROLE_PAIRS.split("|"):
                if ":" in raw:
                    left, right = raw.split(":", maxsplit=1)
                    pairs.add((left.strip().lower(), right.strip().lower()))
                    pairs.add((right.strip().lower(), left.strip().lower()))
            return pairs


        @router.post("/roles")
        def create_role(payload: RolIn, db: Session = Depends(get_db)):
            if db.query(Rol).filter(Rol.nombre.ilike(payload.nombre)).first():
                raise HTTPException(status_code=409, detail="El rol ya existe")
            row = Rol(nombre=payload.nombre, descripcion=payload.descripcion)
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data=RolOut.model_validate(row).model_dump(mode="json"), message="Rol creado")


        @router.get("/roles")
        def list_roles(db: Session = Depends(get_db)):
            rows = db.query(Rol).order_by(Rol.nombre.asc()).all()
            data = [RolOut.model_validate(x).model_dump(mode="json") for x in rows]
            return build_success_response(data=data, message="Roles listados")


        @router.put("/roles/{rol_id}")
        def update_role(rol_id: int, payload: RolIn, db: Session = Depends(get_db)):
            row = db.query(Rol).filter(Rol.id == rol_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Rol no encontrado")
            row.nombre = payload.nombre
            row.descripcion = payload.descripcion
            db.commit()
            db.refresh(row)
            return build_success_response(data=RolOut.model_validate(row).model_dump(mode="json"), message="Rol actualizado")


        @router.post("/roles/{rol_id}/desactivar")
        def deactivate_role(rol_id: int, db: Session = Depends(get_db)):
            row = db.query(Rol).filter(Rol.id == rol_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Rol no encontrado")
            row.estado = "inactivo"
            db.commit()
            return build_success_response(data={"rol_id": rol_id}, message="Rol desactivado")


        @router.post("/permisos")
        def create_permission(payload: PermisoIn, db: Session = Depends(get_db)):
            if db.query(Permiso).filter(Permiso.codigo == payload.codigo).first():
                raise HTTPException(status_code=409, detail="El codigo de permiso ya existe")
            row = Permiso(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data=PermisoOut.model_validate(row).model_dump(mode="json"), message="Permiso creado")


        @router.get("/permisos")
        def list_permissions(db: Session = Depends(get_db)):
            rows = db.query(Permiso).order_by(Permiso.modulo.asc(), Permiso.codigo.asc()).all()
            data = [PermisoOut.model_validate(x).model_dump(mode="json") for x in rows]
            return build_success_response(data=data, message="Permisos listados")


        @router.put("/permisos/{permiso_id}")
        def update_permission(permiso_id: int, payload: PermisoIn, db: Session = Depends(get_db)):
            row = db.query(Permiso).filter(Permiso.id == permiso_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Permiso no encontrado")
            for key, value in payload.model_dump().items():
                setattr(row, key, value)
            db.commit()
            db.refresh(row)
            return build_success_response(data=PermisoOut.model_validate(row).model_dump(mode="json"), message="Permiso actualizado")


        @router.delete("/permisos/{permiso_id}")
        def delete_permission(permiso_id: int, db: Session = Depends(get_db)):
            row = db.query(Permiso).filter(Permiso.id == permiso_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Permiso no encontrado")
            db.query(RolPermiso).filter(RolPermiso.permiso_id == permiso_id).delete()
            db.delete(row)
            db.commit()
            return build_success_response(data={"permiso_id": permiso_id}, message="Permiso eliminado")


        @router.post("/roles/{rol_id}/permisos")
        def assign_permissions_to_role(rol_id: int, payload: AssignPermisosIn, db: Session = Depends(get_db)):
            role = db.query(Rol).filter(Rol.id == rol_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Rol no encontrado")
            for permiso_id in payload.permiso_ids:
                if not db.query(Permiso).filter(Permiso.id == permiso_id).first():
                    raise HTTPException(status_code=404, detail=f"Permiso no encontrado: {permiso_id}")
                exists = db.query(RolPermiso).filter(and_(RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso_id)).first()
                if not exists:
                    db.add(RolPermiso(rol_id=rol_id, permiso_id=permiso_id, assigned_by=payload.assigned_by))
            db.commit()
            return build_success_response(data={"rol_id": rol_id, "permiso_ids": payload.permiso_ids}, message="Permisos asignados")


        @router.delete("/roles/{rol_id}/permisos/{permiso_id}")
        def remove_permission_from_role(rol_id: int, permiso_id: int, db: Session = Depends(get_db)):
            row = db.query(RolPermiso).filter(and_(RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso_id)).first()
            if not row:
                raise HTTPException(status_code=404, detail="Asignacion no encontrada")
            db.delete(row)
            db.commit()
            return build_success_response(data={"rol_id": rol_id, "permiso_id": permiso_id}, message="Permiso removido del rol")


        @router.post("/usuarios/{usuario_id}/roles")
        def assign_role_to_user(usuario_id: int, payload: AssignRolUsuarioIn, db: Session = Depends(get_db)):
            role = db.query(Rol).filter(Rol.id == payload.rol_id, Rol.estado == "activo").first()
            if not role:
                raise HTTPException(status_code=404, detail="Rol no encontrado o inactivo")
            assigned = db.query(UsuarioRol).join(Rol, Rol.id == UsuarioRol.rol_id).filter(
                UsuarioRol.usuario_id == usuario_id, UsuarioRol.estado == "activo"
            ).all()
            pair_set = _contradictory_pairs()
            for current in assigned:
                current_role = db.query(Rol).filter(Rol.id == current.rol_id).first()
                if current_role and (current_role.nombre.lower(), role.nombre.lower()) in pair_set:
                    raise HTTPException(status_code=409, detail="Asignacion de rol contradictoria")
            existing = db.query(UsuarioRol).filter(
                UsuarioRol.usuario_id == usuario_id, UsuarioRol.rol_id == payload.rol_id
            ).first()
            if existing:
                existing.estado = "activo"
                existing.assigned_by = payload.assigned_by
            else:
                db.add(UsuarioRol(usuario_id=usuario_id, rol_id=payload.rol_id, assigned_by=payload.assigned_by, estado="activo"))
            db.commit()
            return build_success_response(data={"usuario_id": usuario_id, "rol_id": payload.rol_id}, message="Rol asignado al usuario")


        @router.get("/usuarios/{usuario_id}/roles")
        def list_user_roles(usuario_id: int, db: Session = Depends(get_db)):
            rows = db.query(UsuarioRol, Rol).join(Rol, Rol.id == UsuarioRol.rol_id).filter(
                UsuarioRol.usuario_id == usuario_id, UsuarioRol.estado == "activo"
            ).all()
            data = [
                {"rol_id": role.id, "nombre": role.nombre, "estado_asignacion": rel.estado, "assigned_at": rel.assigned_at.isoformat() if rel.assigned_at else None}
                for rel, role in rows
            ]
            return build_success_response(data=data, message="Roles del usuario")


        @router.delete("/usuarios/{usuario_id}/roles")
        def remove_user_role(usuario_id: int, payload: RemoveRolUsuarioIn, db: Session = Depends(get_db)):
            row = db.query(UsuarioRol).filter(
                UsuarioRol.usuario_id == usuario_id, UsuarioRol.rol_id == payload.rol_id, UsuarioRol.estado == "activo"
            ).first()
            if not row:
                raise HTTPException(status_code=404, detail="Asignacion de rol no encontrada")
            row.estado = "inactivo"
            db.commit()
            return build_success_response(data={"usuario_id": usuario_id, "rol_id": payload.rol_id}, message="Rol removido del usuario")


        @router.get("/validar-permiso")
        def validate_permission(rol_id: int = Query(...), codigo_permiso: str = Query(...), db: Session = Depends(get_db)):
            role = db.query(Rol).filter(Rol.id == rol_id, Rol.estado == "activo").first()
            if not role:
                return build_success_response(data={"autorizado": False}, message="Rol no valido")
            permiso = db.query(Permiso).filter(Permiso.codigo == codigo_permiso).first()
            if not permiso:
                return build_success_response(data={"autorizado": False}, message="Permiso no existe")
            has = db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso.id
            ).first()
            return build_success_response(data={"autorizado": has is not None}, message="Validacion ejecutada")


        @router.get("/permisos/por-modulo")
        def permissions_by_module(db: Session = Depends(get_db)):
            rows = db.query(Permiso).order_by(Permiso.modulo.asc(), Permiso.codigo.asc()).all()
            grouped = defaultdict(list)
            for row in rows:
                grouped[row.modulo].append(PermisoOut.model_validate(row).model_dump(mode="json"))
            return build_success_response(data=grouped, message="Permisos agrupados por modulo")


        @router.get("/internal/usuarios/{usuario_id}/permisos")
        def get_permissions_for_user(usuario_id: int, db: Session = Depends(get_db)):
            query_rows = (
                db.query(Permiso.codigo)
                .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
                .join(UsuarioRol, UsuarioRol.rol_id == RolPermiso.rol_id)
                .filter(UsuarioRol.usuario_id == usuario_id, UsuarioRol.estado == "activo")
                .distinct()
                .all()
            )
            permisos = [x[0] for x in query_rows]
            return build_success_response(data={"usuario_id": usuario_id, "permisos": permisos}, message="Permisos por usuario")
        """
    ),
)

write(
    "ms-usuarios/requirements.txt",
    dedent(
        """\
        fastapi==0.115.0
        uvicorn==0.30.6
        sqlalchemy==2.0.36
        psycopg[binary]==3.2.3
        pydantic==2.9.2
        pydantic-settings==2.6.0
        passlib[bcrypt]==1.7.4
        cryptography==44.0.1
        httpx==0.27.2
        """
    ),
)

write(
    "ms-usuarios/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-usuarios
        SERVICE_CODE=USR
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_usuarios
        ROL_BASE_URL=http://localhost:8002
        AES_SECRET_KEY_BASE64=QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo0NDQ0NDU1NTY2NjY=
        """
    ),
)

write(
    "ms-usuarios/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_usuarios;
        \\c db_usuarios

        CREATE TABLE IF NOT EXISTS usr_usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            rol_principal_id INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS usr_perfiles (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL UNIQUE REFERENCES usr_usuarios(id),
            tipo_documento VARCHAR(20),
            numero_documento VARCHAR(40) UNIQUE,
            primer_nombre VARCHAR(80) NOT NULL,
            segundo_nombre VARCHAR(80),
            primer_apellido VARCHAR(80) NOT NULL,
            segundo_apellido VARCHAR(80),
            fecha_nacimiento DATE,
            genero VARCHAR(20),
            direccion VARCHAR(180),
            ciudad VARCHAR(80),
            departamento VARCHAR(80),
            telefono_fijo VARCHAR(30),
            telefono_movil VARCHAR(30),
            contacto_emergencia VARCHAR(120),
            telefono_emergencia VARCHAR(30),
            biografia TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS usr_historial_estados (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usr_usuarios(id),
            estado_anterior VARCHAR(20),
            estado_nuevo VARCHAR(20) NOT NULL,
            motivo TEXT NOT NULL,
            changed_by INTEGER,
            changed_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)

write(
    "ms-usuarios/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-usuarios"
            SERVICE_CODE: str = "USR"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_usuarios"
            ROL_BASE_URL: str = "http://localhost:8002"
            AES_SECRET_KEY_BASE64: str = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo0NDQ0NDU1NTY2NjY="
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)

write(
    "ms-usuarios/app/core/security.py",
    dedent(
        """\
        import base64

        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from passlib.context import CryptContext

        from app.core.config import settings

        pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


        def hash_password(raw_password: str) -> str:
            return pwd_context.hash(raw_password)


        def verify_password(raw_password: str, password_hash: str) -> bool:
            return pwd_context.verify(raw_password, password_hash)


        def decrypt_aes_base64(cipher_b64: str) -> str:
            raw = base64.b64decode(cipher_b64)
            if len(raw) < 28:
                raise ValueError("Ciphertext invalido")
            key = base64.b64decode(settings.AES_SECRET_KEY_BASE64)
            nonce = raw[:12]
            ciphertext = raw[12:]
            aesgcm = AESGCM(key)
            plain = aesgcm.decrypt(nonce, ciphertext, None)
            return plain.decode("utf-8")
        """
    ),
)

write(
    "ms-usuarios/app/models/entities.py",
    dedent(
        """\
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
        """
    ),
)

write(
    "ms-usuarios/app/schemas/entities.py",
    dedent(
        """\
        from datetime import date, datetime
        from pydantic import BaseModel, ConfigDict, EmailStr


        class UsuarioCreate(BaseModel):
            username: str
            email: EmailStr
            password_encrypted: str
            rol_principal_id: int | None = None


        class UsuarioUpdate(BaseModel):
            email: EmailStr | None = None
            rol_principal_id: int | None = None
            estado: str | None = None


        class UsuarioOut(BaseModel):
            id: int
            username: str
            email: EmailStr
            estado: str
            rol_principal_id: int | None = None
            created_at: datetime | None = None
            updated_at: datetime | None = None
            model_config = ConfigDict(from_attributes=True)


        class PerfilBase(BaseModel):
            tipo_documento: str | None = None
            numero_documento: str | None = None
            primer_nombre: str
            segundo_nombre: str | None = None
            primer_apellido: str
            segundo_apellido: str | None = None
            fecha_nacimiento: date | None = None
            genero: str | None = None
            direccion: str | None = None
            ciudad: str | None = None
            departamento: str | None = None
            telefono_fijo: str | None = None
            telefono_movil: str | None = None
            contacto_emergencia: str | None = None
            telefono_emergencia: str | None = None
            biografia: str | None = None


        class PerfilCreate(PerfilBase):
            usuario_id: int


        class PerfilUpdate(PerfilBase):
            pass


        class PerfilOut(PerfilBase):
            id: int
            usuario_id: int
            created_at: datetime | None = None
            updated_at: datetime | None = None
            model_config = ConfigDict(from_attributes=True)


        class CambioEstadoIn(BaseModel):
            estado_nuevo: str
            motivo: str
            changed_by: int | None = None
        """
    ),
)

write(
    "ms-usuarios/app/db/init_db.py",
    dedent(
        """\
        from app.db.session import Base, engine
        from app.models import entities  # noqa: F401


        def init_db() -> None:
            Base.metadata.create_all(bind=engine)
        """
    ),
)

write(
    "ms-usuarios/app/api/routes/entities.py",
    dedent(
        """\
        import math

        from fastapi import APIRouter, Depends, HTTPException, Query
        from sqlalchemy import or_
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.core.security import decrypt_aes_base64, hash_password
        from app.db.session import get_db
        from app.models.entities import HistorialEstado, Perfil, Usuario
        from app.schemas.entities import CambioEstadoIn, PerfilCreate, PerfilOut, PerfilUpdate, UsuarioCreate, UsuarioOut, UsuarioUpdate

        router = APIRouter(prefix="/usuarios", tags=["ms-usuarios"])


        def _user_to_out(user: Usuario) -> dict:
            return UsuarioOut.model_validate(user).model_dump(mode="json")


        @router.post("")
        def create_user(payload: UsuarioCreate, db: Session = Depends(get_db)):
            if db.query(Usuario).filter(or_(Usuario.username == payload.username, Usuario.email == payload.email)).first():
                raise HTTPException(status_code=409, detail="Usuario o correo ya existe")
            plain = decrypt_aes_base64(payload.password_encrypted)
            user = Usuario(
                username=payload.username,
                email=payload.email,
                password_hash=hash_password(plain),
                rol_principal_id=payload.rol_principal_id,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            db.add(HistorialEstado(usuario_id=user.id, estado_anterior=None, estado_nuevo=user.estado, motivo="Creacion de usuario"))
            db.commit()
            return build_success_response(data=_user_to_out(user), message="Usuario creado")


        @router.get("")
        def list_users(db: Session = Depends(get_db)):
            rows = db.query(Usuario).order_by(Usuario.id.desc()).all()
            return build_success_response(data=[_user_to_out(x) for x in rows], message="Usuarios listados")


        @router.get("/{usuario_id}")
        def get_user(usuario_id: int, db: Session = Depends(get_db)):
            user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return build_success_response(data=_user_to_out(user), message="Usuario consultado")


        @router.put("/{usuario_id}")
        def update_user(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
            user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            data = payload.model_dump(exclude_none=True)
            for key, value in data.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
            return build_success_response(data=_user_to_out(user), message="Usuario actualizado")


        @router.post("/{usuario_id}/desactivar")
        def deactivate_user(usuario_id: int, motivo: str = Query(...), changed_by: int | None = Query(default=None), db: Session = Depends(get_db)):
            user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            anterior = user.estado
            user.estado = "inactivo"
            db.add(HistorialEstado(usuario_id=usuario_id, estado_anterior=anterior, estado_nuevo="inactivo", motivo=motivo, changed_by=changed_by))
            db.commit()
            return build_success_response(data={"usuario_id": usuario_id}, message="Usuario desactivado")


        @router.post("/{usuario_id}/estado")
        def change_state(usuario_id: int, payload: CambioEstadoIn, db: Session = Depends(get_db)):
            user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            anterior = user.estado
            user.estado = payload.estado_nuevo
            db.add(HistorialEstado(
                usuario_id=usuario_id,
                estado_anterior=anterior,
                estado_nuevo=payload.estado_nuevo,
                motivo=payload.motivo,
                changed_by=payload.changed_by,
            ))
            db.commit()
            db.refresh(user)
            return build_success_response(data=_user_to_out(user), message="Estado actualizado")


        @router.get("/{usuario_id}/historial-estados")
        def state_history(usuario_id: int, db: Session = Depends(get_db)):
            rows = db.query(HistorialEstado).filter(HistorialEstado.usuario_id == usuario_id).order_by(HistorialEstado.changed_at.desc()).all()
            data = [
                {
                    "id": x.id,
                    "estado_anterior": x.estado_anterior,
                    "estado_nuevo": x.estado_nuevo,
                    "motivo": x.motivo,
                    "changed_by": x.changed_by,
                    "changed_at": x.changed_at.isoformat() if x.changed_at else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Historial consultado")


        @router.post("/perfiles")
        def create_profile(payload: PerfilCreate, db: Session = Depends(get_db)):
            if not db.query(Usuario).filter(Usuario.id == payload.usuario_id).first():
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            if payload.numero_documento and db.query(Perfil).filter(Perfil.numero_documento == payload.numero_documento).first():
                raise HTTPException(status_code=409, detail="Numero de documento duplicado")
            row = Perfil(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data=PerfilOut.model_validate(row).model_dump(mode="json"), message="Perfil creado")


        @router.get("/{usuario_id}/perfil")
        def get_profile(usuario_id: int, db: Session = Depends(get_db)):
            row = db.query(Perfil).filter(Perfil.usuario_id == usuario_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            return build_success_response(data=PerfilOut.model_validate(row).model_dump(mode="json"), message="Perfil consultado")


        @router.put("/{usuario_id}/perfil")
        def update_profile(usuario_id: int, payload: PerfilUpdate, db: Session = Depends(get_db)):
            row = db.query(Perfil).filter(Perfil.usuario_id == usuario_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            db.commit()
            db.refresh(row)
            return build_success_response(data=PerfilOut.model_validate(row).model_dump(mode="json"), message="Perfil actualizado")


        @router.get("/busqueda/avanzada")
        def advanced_search(
            nombre: str | None = Query(default=None),
            documento: str | None = Query(default=None),
            email: str | None = Query(default=None),
            estado: str | None = Query(default=None),
            ciudad: str | None = Query(default=None),
            page: int = Query(default=1, ge=1),
            size: int = Query(default=10, ge=1, le=100),
            db: Session = Depends(get_db),
        ):
            query = db.query(Usuario, Perfil).outerjoin(Perfil, Perfil.usuario_id == Usuario.id)
            if nombre:
                like = f"%{nombre}%"
                query = query.filter(or_(Perfil.primer_nombre.ilike(like), Perfil.primer_apellido.ilike(like), Usuario.username.ilike(like)))
            if documento:
                query = query.filter(Perfil.numero_documento == documento)
            if email:
                query = query.filter(Usuario.email.ilike(f"%{email}%"))
            if estado:
                query = query.filter(Usuario.estado == estado)
            if ciudad:
                query = query.filter(Perfil.ciudad.ilike(f"%{ciudad}%"))

            total = query.count()
            pages = math.ceil(total / size) if total else 1
            rows = query.order_by(Usuario.id.desc()).offset((page - 1) * size).limit(size).all()
            items = []
            for user, profile in rows:
                item = _user_to_out(user)
                item["perfil"] = PerfilOut.model_validate(profile).model_dump(mode="json") if profile else None
                items.append(item)
            return build_success_response(
                data={"items": items, "page": page, "size": size, "total": total, "total_pages": pages},
                message="Busqueda avanzada ejecutada",
            )


        @router.get("/buscar/email/{email}")
        def find_by_email(email: str, db: Session = Depends(get_db)):
            row = db.query(Usuario).filter(Usuario.email == email).first()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return build_success_response(data=_user_to_out(row), message="Usuario encontrado por email")


        @router.get("/buscar/documento/{numero_documento}")
        def find_by_document(numero_documento: str, db: Session = Depends(get_db)):
            profile = db.query(Perfil).filter(Perfil.numero_documento == numero_documento).first()
            if not profile:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            user = db.query(Usuario).filter(Usuario.id == profile.usuario_id).first()
            return build_success_response(data=_user_to_out(user), message="Usuario encontrado por documento")


        @router.get("/internal/username/{username}")
        def internal_by_username(username: str, db: Session = Depends(get_db)):
            row = db.query(Usuario).filter(Usuario.username == username).first()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return build_success_response(
                data={"id": row.id, "username": row.username, "email": row.email, "password_hash": row.password_hash, "estado": row.estado},
                message="Usuario interno",
            )


        @router.get("/internal/email/{email}")
        def internal_by_email(email: str, db: Session = Depends(get_db)):
            row = db.query(Usuario).filter(Usuario.email == email).first()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return build_success_response(
                data={"id": row.id, "username": row.username, "email": row.email, "password_hash": row.password_hash, "estado": row.estado},
                message="Usuario interno",
            )
        """
    ),
)

write(
    "ms-autenticacion/requirements.txt",
    dedent(
        """\
        fastapi==0.115.0
        uvicorn==0.30.6
        sqlalchemy==2.0.36
        psycopg[binary]==3.2.3
        pydantic==2.9.2
        pydantic-settings==2.6.0
        pyjwt==2.10.1
        cryptography==44.0.1
        passlib[bcrypt]==1.7.4
        httpx==0.27.2
        """
    ),
)

write(
    "ms-autenticacion/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-autenticacion
        SERVICE_CODE=AUTH
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_autenticacion
        USR_BASE_URL=http://localhost:8003
        ROL_BASE_URL=http://localhost:8002
        JWT_SECRET=change-me
        JWT_ALGORITHM=HS256
        AES_SECRET_KEY_BASE64=QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo0NDQ0NDU1NTY2NjY=
        """
    ),
)

write(
    "ms-autenticacion/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_autenticacion;
        \\c db_autenticacion

        CREATE TABLE IF NOT EXISTS auth_sesiones (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            token_jwt TEXT NOT NULL UNIQUE,
            ip VARCHAR(80),
            user_agent VARCHAR(255),
            estado VARCHAR(20) NOT NULL DEFAULT 'activa',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS auth_tokens_aplicacion (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(80) NOT NULL UNIQUE,
            token_encrypted TEXT NOT NULL,
            descripcion TEXT,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_by INTEGER
        );

        CREATE TABLE IF NOT EXISTS auth_historial_accesos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER,
            tipo_evento VARCHAR(40) NOT NULL,
            ip VARCHAR(80),
            user_agent VARCHAR(255),
            request_id VARCHAR(80),
            event_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS auth_intentos_login (
            id SERIAL PRIMARY KEY,
            login_key VARCHAR(120) NOT NULL UNIQUE,
            intentos INTEGER NOT NULL DEFAULT 0,
            bloqueado BOOLEAN NOT NULL DEFAULT FALSE,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)

write(
    "ms-autenticacion/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-autenticacion"
            SERVICE_CODE: str = "AUTH"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_autenticacion"
            USR_BASE_URL: str = "http://localhost:8003"
            ROL_BASE_URL: str = "http://localhost:8002"
            JWT_SECRET: str = "change-me"
            JWT_ALGORITHM: str = "HS256"
            AES_SECRET_KEY_BASE64: str = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo0NDQ0NDU1NTY2NjY="
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)

write(
    "ms-autenticacion/app/core/security.py",
    dedent(
        """\
        import base64
        from datetime import datetime, timezone

        import jwt
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from passlib.context import CryptContext

        from app.core.config import settings

        pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


        def decrypt_aes_base64(cipher_b64: str) -> str:
            raw = base64.b64decode(cipher_b64)
            key = base64.b64decode(settings.AES_SECRET_KEY_BASE64)
            nonce = raw[:12]
            ciphertext = raw[12:]
            return AESGCM(key).decrypt(nonce, ciphertext, None).decode("utf-8")


        def encrypt_aes_base64(plain: str) -> str:
            key = base64.b64decode(settings.AES_SECRET_KEY_BASE64)
            aesgcm = AESGCM(key)
            nonce = b"0123456789ab"
            encrypted = aesgcm.encrypt(nonce, plain.encode("utf-8"), None)
            return base64.b64encode(nonce + encrypted).decode("utf-8")


        def verify_password(raw_password: str, password_hash: str) -> bool:
            return pwd_context.verify(raw_password, password_hash)


        def build_jwt(usuario_id: int, roles: list[str], permisos: list[str]) -> str:
            payload = {
                "sub": str(usuario_id),
                "roles": roles,
                "permisos": permisos,
                "iat": int(datetime.now(timezone.utc).timestamp()),
            }
            return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        """
    ),
)

write(
    "ms-autenticacion/app/models/entities.py",
    dedent(
        """\
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
        """
    ),
)

write(
    "ms-autenticacion/app/schemas/entities.py",
    dedent(
        """\
        from pydantic import BaseModel


        class LoginIn(BaseModel):
            login: str
            password_encrypted: str


        class LogoutIn(BaseModel):
            token: str


        class ValidateSessionIn(BaseModel):
            token: str


        class AppTokenIn(BaseModel):
            service_name: str
            token_plain: str
            descripcion: str | None = None
            updated_by: int | None = None
        """
    ),
)

write(
    "ms-autenticacion/app/db/init_db.py",
    dedent(
        """\
        from app.db.session import Base, engine
        from app.models import entities  # noqa: F401


        def init_db() -> None:
            Base.metadata.create_all(bind=engine)
        """
    ),
)

write(
    "ms-autenticacion/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import datetime

        import httpx
        from fastapi import APIRouter, Depends, HTTPException, Request
        from sqlalchemy.orm import Session

        from app.core.config import settings
        from app.core.middleware import get_current_request_id
        from app.core.responses import build_success_response
        from app.core.security import build_jwt, decrypt_aes_base64, encrypt_aes_base64, verify_password
        from app.db.session import get_db
        from app.models.entities import HistorialAcceso, IntentoLogin, Sesion, TokenAplicacion
        from app.schemas.entities import AppTokenIn, LoginIn, LogoutIn, ValidateSessionIn

        router = APIRouter(tags=["ms-autenticacion"])


        async def _get_user_for_login(login: str) -> dict:
            async with httpx.AsyncClient(timeout=4.0) as client:
                if "@" in login:
                    r = await client.get(f"{settings.USR_BASE_URL}/api/v1/usuarios/internal/email/{login}")
                else:
                    r = await client.get(f"{settings.USR_BASE_URL}/api/v1/usuarios/internal/username/{login}")
                r.raise_for_status()
                return r.json()["data"]


        async def _get_roles_and_permissions(usuario_id: int) -> tuple[list[str], list[str]]:
            async with httpx.AsyncClient(timeout=4.0) as client:
                roles_r = await client.get(f"{settings.ROL_BASE_URL}/api/v1/usuarios/{usuario_id}/roles")
                roles_r.raise_for_status()
                roles_data = roles_r.json()["data"]
                role_names = [x["nombre"] for x in roles_data]
                perms_r = await client.get(f"{settings.ROL_BASE_URL}/api/v1/internal/usuarios/{usuario_id}/permisos")
                perms_r.raise_for_status()
                permisos = perms_r.json()["data"]["permisos"]
                return role_names, permisos


        def _add_access_log(db: Session, usuario_id: int | None, tipo_evento: str, request: Request) -> None:
            db.add(
                HistorialAcceso(
                    usuario_id=usuario_id,
                    tipo_evento=tipo_evento,
                    ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    request_id=get_current_request_id(),
                )
            )
            db.commit()


        @router.post("/login")
        async def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
            tracker = db.query(IntentoLogin).filter(IntentoLogin.login_key == payload.login).first()
            if tracker and tracker.bloqueado:
                _add_access_log(db, None, "bloqueo_cuenta", request)
                raise HTTPException(status_code=423, detail="Cuenta bloqueada por intentos fallidos")

            try:
                user_data = await _get_user_for_login(payload.login)
            except Exception:
                user_data = None

            if not user_data:
                if not tracker:
                    tracker = IntentoLogin(login_key=payload.login, intentos=1, bloqueado=False)
                    db.add(tracker)
                else:
                    tracker.intentos += 1
                    if tracker.intentos >= 5:
                        tracker.bloqueado = True
                db.commit()
                _add_access_log(db, None, "intento_fallido", request)
                raise HTTPException(status_code=401, detail="Credenciales invalidas")

            if user_data["estado"] != "activo":
                raise HTTPException(status_code=403, detail="Usuario no activo")

            plain = decrypt_aes_base64(payload.password_encrypted)
            ok = verify_password(plain, user_data["password_hash"])
            if not ok:
                if not tracker:
                    tracker = IntentoLogin(login_key=payload.login, intentos=1, bloqueado=False)
                    db.add(tracker)
                else:
                    tracker.intentos += 1
                    if tracker.intentos >= 5:
                        tracker.bloqueado = True
                db.commit()
                _add_access_log(db, user_data["id"], "intento_fallido", request)
                raise HTTPException(status_code=401, detail="Credenciales invalidas")

            if tracker:
                tracker.intentos = 0
                tracker.bloqueado = False
                db.commit()

            roles, permisos = await _get_roles_and_permissions(user_data["id"])
            jwt_token = build_jwt(user_data["id"], roles, permisos)
            session = Sesion(
                usuario_id=user_data["id"],
                token_jwt=jwt_token,
                ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                estado="activa",
            )
            db.add(session)
            db.commit()
            _add_access_log(db, user_data["id"], "inicio_sesion", request)
            return build_success_response(data={"token": jwt_token, "usuario_id": user_data["id"], "roles": roles, "permisos": permisos}, message="Login exitoso")


        @router.post("/logout")
        def logout(payload: LogoutIn, request: Request, db: Session = Depends(get_db)):
            row = db.query(Sesion).filter(Sesion.token_jwt == payload.token, Sesion.estado == "activa").first()
            if not row:
                raise HTTPException(status_code=404, detail="Sesion no encontrada")
            row.estado = "cerrada"
            row.last_activity_at = datetime.utcnow()
            db.commit()
            _add_access_log(db, row.usuario_id, "cierre_sesion", request)
            return build_success_response(data={"usuario_id": row.usuario_id}, message="Sesion cerrada")


        @router.post("/validar-sesion")
        def validate_session(payload: ValidateSessionIn, db: Session = Depends(get_db)):
            row = db.query(Sesion).filter(Sesion.token_jwt == payload.token, Sesion.estado == "activa").first()
            if not row:
                return build_success_response(data={"activa": False}, message="Sesion invalida")
            row.last_activity_at = datetime.utcnow()
            db.commit()
            return build_success_response(data={"activa": True, "usuario_id": row.usuario_id}, message="Sesion valida")


        @router.get("/sesiones/activas")
        def active_sessions(usuario_id: int | None = None, db: Session = Depends(get_db)):
            query = db.query(Sesion).filter(Sesion.estado == "activa")
            if usuario_id:
                query = query.filter(Sesion.usuario_id == usuario_id)
            rows = query.order_by(Sesion.created_at.desc()).all()
            data = [
                {
                    "id": x.id,
                    "usuario_id": x.usuario_id,
                    "ip": x.ip,
                    "user_agent": x.user_agent,
                    "created_at": x.created_at.isoformat() if x.created_at else None,
                    "last_activity_at": x.last_activity_at.isoformat() if x.last_activity_at else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Sesiones activas listadas")


        @router.post("/sesiones/{sesion_id}/forzar-cierre")
        def force_close_session(sesion_id: int, db: Session = Depends(get_db)):
            row = db.query(Sesion).filter(Sesion.id == sesion_id, Sesion.estado == "activa").first()
            if not row:
                raise HTTPException(status_code=404, detail="Sesion no encontrada")
            row.estado = "cerrada"
            db.commit()
            return build_success_response(data={"sesion_id": sesion_id}, message="Sesion cerrada por administrador")


        @router.get("/historial-accesos")
        def access_history(
            usuario_id: int | None = None,
            tipo_evento: str | None = None,
            fecha_inicio: str | None = None,
            fecha_fin: str | None = None,
            db: Session = Depends(get_db),
        ):
            query = db.query(HistorialAcceso)
            if usuario_id:
                query = query.filter(HistorialAcceso.usuario_id == usuario_id)
            if tipo_evento:
                query = query.filter(HistorialAcceso.tipo_evento == tipo_evento)
            if fecha_inicio:
                query = query.filter(HistorialAcceso.event_at >= fecha_inicio)
            if fecha_fin:
                query = query.filter(HistorialAcceso.event_at <= fecha_fin)
            rows = query.order_by(HistorialAcceso.event_at.desc()).all()
            data = [
                {
                    "usuario_id": x.usuario_id,
                    "tipo_evento": x.tipo_evento,
                    "ip": x.ip,
                    "user_agent": x.user_agent,
                    "request_id": x.request_id,
                    "event_at": x.event_at.isoformat() if x.event_at else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Historial de accesos")


        @router.post("/tokens-aplicacion")
        def create_app_token(payload: AppTokenIn, db: Session = Depends(get_db)):
            if db.query(TokenAplicacion).filter(TokenAplicacion.service_name == payload.service_name).first():
                raise HTTPException(status_code=409, detail="Token de aplicacion ya existe para ese servicio")
            row = TokenAplicacion(
                service_name=payload.service_name,
                token_encrypted=encrypt_aes_base64(payload.token_plain),
                descripcion=payload.descripcion,
                estado="activo",
                updated_by=payload.updated_by,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id, "service_name": row.service_name, "estado": row.estado}, message="Token de aplicacion creado")


        @router.get("/tokens-aplicacion")
        def list_app_tokens(db: Session = Depends(get_db)):
            rows = db.query(TokenAplicacion).order_by(TokenAplicacion.service_name.asc()).all()
            data = [
                {
                    "id": x.id,
                    "service_name": x.service_name,
                    "descripcion": x.descripcion,
                    "estado": x.estado,
                    "created_at": x.created_at.isoformat() if x.created_at else None,
                    "updated_at": x.updated_at.isoformat() if x.updated_at else None,
                    "updated_by": x.updated_by,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Tokens de aplicacion listados")


        @router.put("/tokens-aplicacion/{token_id}")
        def update_app_token(token_id: int, payload: AppTokenIn, db: Session = Depends(get_db)):
            row = db.query(TokenAplicacion).filter(TokenAplicacion.id == token_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Token de aplicacion no encontrado")
            row.service_name = payload.service_name
            row.token_encrypted = encrypt_aes_base64(payload.token_plain)
            row.descripcion = payload.descripcion
            row.updated_by = payload.updated_by
            db.commit()
            return build_success_response(data={"id": row.id}, message="Token de aplicacion actualizado")


        @router.post("/tokens-aplicacion/{token_id}/desactivar")
        def deactivate_app_token(token_id: int, db: Session = Depends(get_db)):
            row = db.query(TokenAplicacion).filter(TokenAplicacion.id == token_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Token de aplicacion no encontrado")
            row.estado = "inactivo"
            db.commit()
            return build_success_response(data={"id": row.id}, message="Token de aplicacion desactivado")
        """
    ),
)

print("Modulo 1 implementado (roles, usuarios, autenticacion).")
