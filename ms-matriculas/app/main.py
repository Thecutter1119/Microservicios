import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.entities import router as entities_router
from app.core.config import settings
from app.core.middleware import RequestIdMiddleware, get_current_request_id
from app.core.responses import build_error_response, build_success_response
from app.db.init_db import init_db

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ms-matriculas",
    description="Microservicio ERP Universitario - MAT",
    version="1.0.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(RequestIdMiddleware)
app.include_router(entities_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    payload = build_error_response(message=str(exc.detail)).model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers={"X-Request-ID": get_current_request_id()},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = build_error_response(
        message="Error de validacion",
        data={"errors": exc.errors()},
    ).model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return JSONResponse(
        status_code=422,
        content=payload,
        headers={"X-Request-ID": get_current_request_id()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Error interno no manejado")
    payload = build_error_response(message="Error interno del servidor").model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    return JSONResponse(
        status_code=500,
        content=payload,
        headers={"X-Request-ID": get_current_request_id()},
    )


@app.get("/health")
def health_check():
    return build_success_response(
        data={"status": "ok", "service": settings.PROJECT_NAME},
        message="Servicio operativo",
    )
