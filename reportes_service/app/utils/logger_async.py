"""
ms-reportes [REP] — Logger de Auditoría Asíncrona
REP-RF-004: Registro de Auditoría Asíncrona (fire-and-forget)
Patrón: la respuesta HTTP ya viajó al usuario antes de iniciar este envío.
"""

import logging
import time
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.security import outgoing_headers

logger = logging.getLogger("ms-reportes.auditoria")


def build_log_entry(
    request_id: str,
    funcionalidad: str,
    metodo_http: str,
    endpoint: str,
    codigo_respuesta: int,
    duracion_ms: int,
    usuario_id: int | None,
    detalle: dict | None = None,
) -> dict:
    """
    Construye el objeto JSON del log según el contrato definido en §3.6
    del Diseño de Integración.
    """
    return {
        "fecha_hora": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "microservicio": settings.SERVICE_CODE,
        "funcionalidad": funcionalidad,
        "metodo_http": metodo_http,
        "endpoint": endpoint,
        "codigo_respuesta": codigo_respuesta,
        "duracion_ms": duracion_ms,
        "usuario_id": usuario_id,
        "detalle": detalle or {},
    }


async def send_audit_log(log_entry: dict, request_id: str) -> None:
    """
    Envía el log de auditoría a ms-auditoria de forma asíncrona.
    Timeout: 2 segundos. Si falla, registra WARNING en log local y continúa.
    REP-RF-004 — fire-and-forget.
    """
    url = f"{settings.MS_AUDITORIA_URL}/api/v1/logs"
    headers = outgoing_headers(request_id)

    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_AUDIT) as client:
            response = await client.post(url, json=log_entry, headers=headers)
            if response.status_code not in (200, 201):
                logger.warning(
                    "Fallo de auditoría — request_id=%s causa=HTTP_%s funcionalidad=%s",
                    request_id,
                    response.status_code,
                    log_entry.get("funcionalidad"),
                )
    except httpx.TimeoutException:
        logger.warning(
            "Fallo de auditoría — request_id=%s causa=timeout funcionalidad=%s",
            request_id,
            log_entry.get("funcionalidad"),
        )
    except Exception as exc:
        logger.warning(
            "Fallo de auditoría — request_id=%s causa=%s funcionalidad=%s",
            request_id,
            str(exc),
            log_entry.get("funcionalidad"),
        )
