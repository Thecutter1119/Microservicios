from datetime import datetime, timezone
from time import perf_counter

from fastapi import Request
from starlette.responses import Response

from app.infrastructure.clients.auditoria_client import fire_and_forget_audit


async def audit_middleware(request: Request, call_next) -> Response:
    start = perf_counter()
    response = await call_next(request)
    duration_ms = int((perf_counter() - start) * 1000)
    request_id = getattr(request.state, "request_id", "DOM-unknown")

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "microservice": "ms-domicilios",
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
        "user_id": getattr(request.state, "user_id", request.headers.get("X-User-ID")),
    }
    fire_and_forget_audit(payload)
    return response
