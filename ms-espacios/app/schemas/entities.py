from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class TipoEspacioIn(BaseModel):
    nombre: str
    descripcion: str | None = None
    requiere_equipamiento_especial: bool = False
    estado: str = "activo"


class TipoEspacioOut(TipoEspacioIn):
    id: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class EspacioIn(BaseModel):
    codigo: str
    nombre: str
    tipo_espacio_id: int
    edificio: str
    piso: int | None = None
    capacidad_maxima: int
    estado: str = "disponible"
    descripcion: str | None = None


class EspacioUpdate(BaseModel):
    nombre: str | None = None
    tipo_espacio_id: int | None = None
    edificio: str | None = None
    piso: int | None = None
    capacidad_maxima: int | None = None
    estado: str | None = None
    descripcion: str | None = None


class EspacioOut(EspacioIn):
    id: int
    fecha_registro: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class EstadoEspacioIn(BaseModel):
    estado: str
    motivo: str
    changed_by: int | None = None


class EquipamientoIn(BaseModel):
    espacio_id: int
    activo_id: int
    cantidad: int


class MantenimientoIn(BaseModel):
    espacio_id: int
    descripcion: str
    responsable_id: int | None = None
    costo_estimado: float | None = None
    fecha_programada: datetime
    estado: str = "programado"
    observaciones: str | None = None


class MantenimientoUpdate(BaseModel):
    descripcion: str | None = None
    responsable_id: int | None = None
    costo_estimado: float | None = None
    fecha_programada: datetime | None = None
    fecha_ejecucion_real: datetime | None = None
    estado: str | None = None
    observaciones: str | None = None


class OcupacionIn(BaseModel):
    espacio_id: int
    fecha: date
    horas_ocupadas: float
    horas_disponibles: float
    periodo: str
