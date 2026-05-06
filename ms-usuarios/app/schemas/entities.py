from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str | None = None
    password_encrypted: str | None = None
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
