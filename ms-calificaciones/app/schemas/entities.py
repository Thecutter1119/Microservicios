from datetime import date
from pydantic import BaseModel, Field


class CorteIn(BaseModel):
    asignatura_id: int
    periodo_id: int
    nombre: str
    porcentaje: float = Field(ge=0, le=100)
    numero_corte: int
    fecha_inicio: date
    fecha_fin: date


class NotaIn(BaseModel):
    inscripcion_id: int
    corte_id: int
    nota: float = Field(ge=0, le=5)
    observaciones: str | None = None
    registrado_por: int | None = None
