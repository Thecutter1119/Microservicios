from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes.entregas import router as entregas_router
from app.api.routes.health import router as health_router
from app.api.routes.repartidores import router as repartidores_router
from app.core.audit_middleware import audit_middleware
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.request_id import request_id_middleware
import app.domain.models  # noqa: F401

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(BaseHTTPMiddleware, dispatch=request_id_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=audit_middleware)
app.include_router(health_router)
app.include_router(repartidores_router)
app.include_router(entregas_router)
register_exception_handlers(app)
