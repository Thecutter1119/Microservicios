from datetime import date
from pydantic import BaseModel


class PeriodoIn(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    fecha_inicio_inscripciones: date
    fecha_fin_inscripciones: date
    estado: str = "planificado"


class MatriculaIn(BaseModel):
    estudiante_id: int
    periodo_id: int
    programa_id: int
    semestre_actual: int
    estado: str = "activa"


class InscripcionIn(BaseModel):
    matricula_id: int
    asignatura_id: int
    franja_horaria_id: int | None = None
