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
