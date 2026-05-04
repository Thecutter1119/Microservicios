from datetime import time
from pydantic import BaseModel


class FranjaIn(BaseModel):
    asignatura_id: int
    docente_id: int
    espacio_id: int
    periodo: str
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    grupo: str
    estado: str = "activa"


class FranjaUpdate(BaseModel):
    docente_id: int | None = None
    espacio_id: int | None = None
    periodo: str | None = None
    dia_semana: str | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None
    grupo: str | None = None
    estado: str | None = None


class AsignacionDocenteIn(BaseModel):
    docente_id: int
    asignatura_id: int
    periodo: str
    grupo: str
    horas_semanales: int
    estado: str = "activa"
