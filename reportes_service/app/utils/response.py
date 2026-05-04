"""
ms-reportes [REP] — Constructor de respuesta estándar
REP-RF-005: Estructura de Respuesta Estándar
Formato: { request_id, success, data, message, timestamp }
"""

from datetime import datetime, timezone
from typing import Any
from fastapi import Response
from fastapi.responses import JSONResponse


def std_response(
    request_id: str,
    success: bool,
    data: Any,
    message: str,
    http_status: int = 200,
    extra_headers: dict | None = None,
) -> JSONResponse:
    """
    Construye la respuesta estándar de ms-reportes.
    Incluye X-Request-ID en headers (REP-RF-003 paso 6).
    """
    body = {
        "request_id": request_id,
        "success": success,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    headers = {"X-Request-ID": request_id}
    if extra_headers:
        headers.update(extra_headers)
    return JSONResponse(content=body, status_code=http_status, headers=headers)


def paginated_response(
    request_id: str,
    data: list,
    total: int,
    pagina: int,
    por_pagina: int,
    message: str = "Consulta exitosa",
    http_status: int = 200,
) -> JSONResponse:
    """Respuesta paginada estándar."""
    import math
    body = {
        "request_id": request_id,
        "success": True,
        "data": data,
        "paginacion": {
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total": total,
            "paginas": math.ceil(total / por_pagina) if por_pagina > 0 else 0,
        },
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(content=body, status_code=http_status, headers={"X-Request-ID": request_id})
