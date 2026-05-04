"""
ms-reportes [REP] — Punto de entrada principal
Módulo 6 — Transversales | FastAPI + Python + PostgreSQL
Base URL: /api/v1
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Importar modelos para que SQLAlchemy los registre antes del create_all
from app.models import plantilla, reporte, programacion  # noqa: F401

from app.routers import plantilla_router, reporte_router, programacion_router
from app.services.scheduler_service import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("ms-reportes")

# Ruta al index.html (un nivel arriba de /app)
_frontend = Path(__file__).resolve().parent.parent / "index.html"
_appjs = Path(__file__).resolve().parent.parent / "app.js"


# ── Lifespan: startup / shutdown ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("═══ ms-reportes [REP] iniciando ═══")
    log.info("Versión: %s | Módulo: %s", settings.SERVICE_VERSION, settings.MODULE)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Base de datos: tablas verificadas/creadas")

    start_scheduler()

    yield

    stop_scheduler()
    await engine.dispose()
    log.info("═══ ms-reportes [REP] detenido ═══")


# ── Aplicación FastAPI ────────────────────────────────────────────────────────

app = FastAPI(
    title="ms-reportes [REP]",
    description=(
        "Microservicio de generación consolidada de reportes institucionales. "
        "Gestiona plantillas, reportes y programaciones automáticas. "
        "Módulo 6 — Transversales."
    ),
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Content-Disposition"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(plantilla_router.router)
app.include_router(reporte_router.router)
app.include_router(programacion_router.router)


# ── Manejador global de excepciones ──────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from app.core.security import resolve_request_id
    request_id = resolve_request_id(request)
    log.error("Error no manejado request_id=%s: %s", request_id, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "request_id": request_id,
            "success": False,
            "data": None,
            "message": "Error interno del servidor",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        headers={"X-Request-ID": request_id},
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Sistema"])
async def health(request: Request):
    """Health check — confirma que el servicio está operativo."""
    from app.core.security import resolve_request_id
    request_id = resolve_request_id(request)
    return JSONResponse(
        content={
            "request_id": request_id,
            "success": True,
            "data": {
                "service": settings.SERVICE_NAME,
                "code": settings.SERVICE_CODE,
                "version": settings.SERVICE_VERSION,
                "module": settings.MODULE,
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "message": "ms-reportes operativo",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        headers={"X-Request-ID": request_id},
    )


# ── Firma JSON del microservicio (para consumo programático) ──────────────────

@app.get("/info", tags=["Sistema"])
async def firma():
    """
    Firma del microservicio ms-reportes [REP].
    Retorna identidad, versión, módulo y catálogo de endpoints en JSON.
    """
    return JSONResponse(content={
        "microservicio": settings.SERVICE_NAME,
        "codigo": settings.SERVICE_CODE,
        "version": settings.SERVICE_VERSION,
        "modulo": settings.MODULE,
        "stack": "FastAPI + Python + PostgreSQL",
        "base_url": "https://api.universidad.edu/api/v1",
        "base_datos": "db_reportes",
        "descripcion": (
            "Orquestador de reportes institucionales consolidados. "
            "Gestiona plantillas, genera reportes desde múltiples fuentes "
            "y administra programaciones automáticas periódicas."
        ),
        "integraciones": {
            "autenticacion": "ms-autenticacion [AUT] — validación de sesión (síncrono)",
            "roles": "ms-roles [ROL] — verificación de permisos (síncrono)",
            "fuentes": [
                "ms-calificaciones [CAL]",
                "ms-inventario [INV]",
                "ms-presupuesto [PRE]",
            ],
            "auditoria": "ms-auditoria [AUD] — fire-and-forget (asíncrono)",
        },
        "endpoints": {
            "plantillas": [
                "POST   /api/v1/plantillas           — REP-RF-006",
                "GET    /api/v1/plantillas           — REP-RF-008",
                "GET    /api/v1/plantillas/{id}      — REP-RF-007",
                "PUT    /api/v1/plantillas/{id}      — REP-RF-009",
                "DELETE /api/v1/plantillas/{id}      — REP-RF-010",
            ],
            "reportes": [
                "POST   /api/v1/reportes                      — REP-RF-011",
                "GET    /api/v1/reportes                      — REP-RF-021",
                "GET    /api/v1/reportes/{id}                 — REP-RF-013",
                "GET    /api/v1/reportes/{id}/descargar       — REP-RF-014",
                "POST   /api/v1/reportes/{id}/invalidar-cache — REP-RF-022",
            ],
            "programaciones": [
                "POST   /api/v1/programaciones                    — REP-RF-015",
                "GET    /api/v1/programaciones                    — REP-RF-016",
                "GET    /api/v1/programaciones/{id}               — REP-RF-024",
                "PUT    /api/v1/programaciones/{id}               — REP-RF-017",
                "POST   /api/v1/programaciones/{id}/desactivar    — REP-RF-018",
                "POST   /api/v1/programaciones/{id}/reactivar     — REP-RF-023",
                "POST   /api/v1/programaciones/{id}/ejecutar      — REP-RF-020",
            ],
            "sistema": [
                "GET    /         — Panel frontend (index.html)",
                "GET    /info     — Firma JSON del microservicio",
                "GET    /health   — Health check",
                "GET    /docs     — Swagger UI",
                "GET    /redoc    — ReDoc",
            ],
        },
        "requisitos": {
            "total": 24,
            "transversales": "REP-RF-001 a REP-RF-005",
            "plantillas": "REP-RF-006 a REP-RF-010",
            "reportes": "REP-RF-011 a REP-RF-014",
            "programaciones": "REP-RF-015 a REP-RF-020",
            "sugeridos": "REP-RF-021 a REP-RF-024",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ── Raíz / — sirve el panel frontend directamente ────────────────────────────

@app.get("/", tags=["Sistema"], include_in_schema=False)
async def frontend():
    """Sirve el panel frontend ReportEngine (index.html)."""
    if _frontend.exists():
        return FileResponse(str(_frontend), media_type="text/html")
    return JSONResponse(
        {"error": "index.html no encontrado en la raíz del proyecto"},
        status_code=404,
    )


@app.get("/app.js", tags=["Sistema"], include_in_schema=False)
async def appjs():
    """Sirve el JavaScript del panel frontend (app.js)."""
    if _appjs.exists():
        return FileResponse(str(_appjs), media_type="application/javascript")
    return JSONResponse({"error": "app.js no encontrado"}, status_code=404)
