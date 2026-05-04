from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging
from fastapi import BackgroundTasks
import httpx
from app.core.middleware import get_current_request_id
from app.core.config import settings

DataT = TypeVar('DataT')

logger = logging.getLogger(__name__)

class StandardResponse(BaseModel, Generic[DataT]):
    request_id: str = Field(default_factory=get_current_request_id)
    success: bool
    data: Optional[DataT] = None
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

def build_success_response(data: Any, message: str = "Operación exitosa") -> StandardResponse:
    return StandardResponse(
        success=True,
        data=data,
        message=message
    )

def build_error_response(message: str, data: Any = None) -> StandardResponse:
    return StandardResponse(
        success=False,
        data=data,
        message=message
    )

async def send_audit_log_task(
    request_id: str,
    funcionalidad: str,
    metodo: str,
    status_code: int,
    duracion_ms: int,
    usuario_id: Optional[int] = None,
    detalle: str = ""
):
    payload = {
        "fecha_hora": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "microservicio": settings.PROJECT_NAME,
        "funcionalidad": funcionalidad,
        "metodo": metodo,
        "codigo_respuesta": status_code,
        "duracion_ms": duracion_ms,
        "usuario_id": usuario_id,
        "detalle": detalle
    }
    
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{settings.AUD_BASE_URL}/api/v1/auditoria/logs",
                json=payload,
                headers={"X-App-Token": settings.PED_APP_TOKEN}
            )
    except Exception as e:
        logger.warning("AUDIT_FAIL: %s", str(e))

def add_audit_task(
    background_tasks: BackgroundTasks,
    funcionalidad: str,
    metodo: str,
    status_code: int,
    duracion_ms: int,
    usuario_id: Optional[int] = None,
    detalle: str = ""
):
    request_id = get_current_request_id()
    background_tasks.add_task(
        send_audit_log_task,
        request_id=request_id,
        funcionalidad=funcionalidad,
        metodo=metodo,
        status_code=status_code,
        duracion_ms=duracion_ms,
        usuario_id=usuario_id,
        detalle=detalle
    )
