from datetime import time
from pydantic import BaseModel


class NotificacionIn(BaseModel):
    usuario_id: int
    canal: str
    asunto: str | None = None
    mensaje: str
    prioridad: str = "normal"
    max_intentos: int = 3
    request_id: str | None = None


class NotificacionPlantillaIn(BaseModel):
    usuario_id: int
    plantilla_id: int
    variables: dict[str, str]
    prioridad: str = "normal"
    max_intentos: int = 3
    request_id: str | None = None


class PlantillaIn(BaseModel):
    nombre: str
    canal: str
    asunto_template: str | None = None
    mensaje_template: str
    variables_requeridas: list[str] | None = None
    estado: str = "activo"


class PreferenciaIn(BaseModel):
    usuario_id: int
    canal_preferido: str
    notificaciones_activas: bool = True
    no_molestar_inicio: time | None = None
    no_molestar_fin: time | None = None
