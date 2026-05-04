from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReservaIn(BaseModel):
    espacio_id: int
    usuario_id: int
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_fin: datetime


class ReservaUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None


class CancelReservaIn(BaseModel):
    motivo: str
    cancelled_by: int | None = None


class ReservaOut(BaseModel):
    id: int
    espacio_id: int
    usuario_id: int
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str
    created_at: datetime | None = None
    cancelled_by: int | None = None
    motivo_cancelacion: str | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class PoliticaIn(BaseModel):
    nombre: str
    min_anticipacion_horas: int
    max_anticipacion_dias: int
    duracion_max_horas: int
    limite_cancelacion_horas: int
    max_reservas_activas_usuario: int
    estado: str = "activo"


class BloqueoIn(BaseModel):
    espacio_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    motivo: str
    created_by: int | None = None
