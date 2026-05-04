from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime, timezone
import logging
from app.core.middleware import RequestIdMiddleware, get_current_request_id
from app.core.config import settings
from app.api.routes import pedidos
from app.core.responses import build_error_response

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ms-pedidos",
    description="Microservicio de Gestión de Pedidos - ERP Universitario",
    version="1.0.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(RequestIdMiddleware)

app.include_router(pedidos.router, prefix=settings.API_V1_STR)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    payload = build_error_response(message=str(exc.detail)).model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers={"X-Request-ID": get_current_request_id()}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = build_error_response(message="Error de validación de datos", data={"errors": exc.errors()}).model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return JSONResponse(
        status_code=422,
        content=payload,
        headers={"X-Request-ID": get_current_request_id()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Error interno no manejado")
    payload = build_error_response(message="Error interno del servidor").model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return JSONResponse(
        status_code=500,
        content=payload,
        headers={"X-Request-ID": get_current_request_id()}
    )

@app.get("/health")
def health_check():
    from app.core.responses import build_success_response
    return build_success_response(data={"status": "ok"}, message="Servicio ms-pedidos funcionando correctamente")
