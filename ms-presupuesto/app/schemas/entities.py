from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PresupuestoIn(BaseModel):
    nombre: str
    periodo: str
    monto_total: float


class PresupuestoUpdate(BaseModel):
    nombre: str | None = None
    periodo: str | None = None
    monto_total: float | None = None
    estado: str | None = None


class PartidaIn(BaseModel):
    presupuesto_id: int
    nombre: str
    area_destino: str
    monto_asignado: float
    porcentaje_alerta: int = 80
    estado: str = "activo"


class PartidaUpdate(BaseModel):
    nombre: str | None = None
    area_destino: str | None = None
    monto_asignado: float | None = None
    porcentaje_alerta: int | None = None
    estado: str | None = None


class ReasignacionIn(BaseModel):
    partida_origen_id: int
    partida_destino_id: int
    monto: float
    motivo: str
    solicitado_por: int | None = None
