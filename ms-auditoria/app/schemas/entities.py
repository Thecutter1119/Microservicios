from datetime import datetime
from pydantic import BaseModel


class EventoIn(BaseModel):
    fecha_hora: datetime | None = None
    request_id: str | None = None
    microservicio: str
    funcionalidad: str | None = None
    metodo: str | None = None
    codigo_respuesta: int | None = None
    duracion_ms: int | None = None
    usuario_id: int | None = None
    detalle: str | None = None


class RetencionIn(BaseModel):
    dias_retencion: int
    estado: str = "activa"
