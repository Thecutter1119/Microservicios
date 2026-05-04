from datetime import date
from pydantic import BaseModel


class ProgramaIn(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None
    duracion_semestres: int
    total_creditos_requeridos: int
    estado: str = "activo"
    coordinador_usuario_id: int | None = None


class AsignaturaIn(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None
    creditos: int
    semestre_sugerido: int
    programa_id: int
    horas_semanales: int
    tipo: str
    estado: str = "activo"


class PrerrequisitoIn(BaseModel):
    asignatura_id: int
    prerrequisito_id: int
    tipo: str


class MallaVersionIn(BaseModel):
    programa_id: int
    version_identificador: str
    fecha_vigencia_inicio: date
    fecha_vigencia_fin: date | None = None
    estado: str = "borrador"
    descripcion_cambios: str | None = None
    creado_por: int | None = None
