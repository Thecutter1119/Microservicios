"""
ms-reportes [REP] — Router: Reportes
Endpoints:
  POST   /api/v1/reportes                       → REP-RF-011
  GET    /api/v1/reportes                       → REP-RF-021
  GET    /api/v1/reportes/{id}                  → REP-RF-013
  GET    /api/v1/reportes/{id}/descargar        → REP-RF-014
  POST   /api/v1/reportes/{id}/invalidar-cache  → REP-RF-022
"""

import time
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Request, BackgroundTasks, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import resolve_request_id
from app.db.database import get_db
from app.schemas.reporte_schema import ReporteCreate, ReporteOut
from app.services.microservice_client import autenticar_y_autorizar
from app.services.reporte_service import (
    solicitar_reporte, consultar_estado_reporte,
    descargar_reporte, listar_reportes, invalidar_cache,
)
from app.utils.csv_generator import build_content_disposition
from app.utils.logger_async import build_log_entry, send_audit_log
from app.utils.response import std_response, paginated_response

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])
log = logging.getLogger("ms-reportes.router.reportes")


def _token(request: Request) -> str:
    return request.headers.get("Authorization", "").replace("Bearer ", "").strip()


# ── POST /api/v1/reportes ─────────────────────────────────────────────────────

@router.post("")
async def solicitar(
    request: Request,
    body: ReporteCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-011: Solicitar Generación de Reporte (200 caché | 202 async)"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:REPORTES:SOLICITAR", request_id)

    reporte, desde_cache = await solicitar_reporte(db, body, usuario.get("usuario_id", 0), request_id)

    http_status = 200 if desde_cache else 202
    mensaje = "Reporte obtenido desde caché" if desde_cache else "Generación de reporte iniciada"
    data = {
        "reporte_id": reporte.id,
        "estado": reporte.estado,
        "desde_cache": desde_cache,
    }

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-011", "POST", "/api/v1/reportes", http_status, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, mensaje, http_status)


# ── GET /api/v1/reportes ──────────────────────────────────────────────────────

@router.get("")
async def listar(
    request: Request,
    background_tasks: BackgroundTasks,
    estado: str | None = Query(None),
    plantilla_id: int | None = Query(None),
    solicitado_por: int | None = Query(None),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-021: Listar Reportes Generados (sin resultado_cache)"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:REPORTES:LISTAR", request_id)

    reportes, total = await listar_reportes(
        db, estado, plantilla_id, solicitado_por, fecha_desde, fecha_hasta, pagina, por_pagina
    )
    data = [ReporteOut.model_validate(r).model_dump(mode="json") for r in reportes]

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-021", "GET", "/api/v1/reportes", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return paginated_response(request_id, data, total, pagina, por_pagina, "Reportes obtenidos exitosamente")


# ── GET /api/v1/reportes/{id} ─────────────────────────────────────────────────

@router.get("/{reporte_id}")
async def consultar_estado(
    reporte_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-013: Consultar Estado de Reporte (sin resultado_cache)"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:REPORTES:CONSULTAR", request_id)

    reporte = await consultar_estado_reporte(db, reporte_id)
    data = ReporteOut.model_validate(reporte).model_dump(mode="json")

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-013", "GET", f"/api/v1/reportes/{reporte_id}", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, "Estado del reporte obtenido")


# ── GET /api/v1/reportes/{id}/descargar ──────────────────────────────────────

@router.get("/{reporte_id}/descargar")
async def descargar(
    reporte_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-014: Descargar Reporte Generado"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:REPORTES:DESCARGAR", request_id)

    reporte, contenido = await descargar_reporte(db, reporte_id)

    fmt = reporte.formato_salida.upper()
    content_type = "text/csv; charset=utf-8" if fmt == "CSV" else "application/json"
    ext = "csv" if fmt == "CSV" else "json"
    disposition = build_content_disposition(reporte.nombre, ext)

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-014", "GET", f"/api/v1/reportes/{reporte_id}/descargar", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return Response(
        content=contenido,
        media_type=content_type,
        headers={
            "Content-Disposition": disposition,
            "X-Request-ID": request_id,
        },
    )


# ── POST /api/v1/reportes/{id}/invalidar-cache ───────────────────────────────

@router.post("/{reporte_id}/invalidar-cache")
async def invalidar(
    reporte_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-022: Invalidar Caché de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:REPORTES:INVALIDAR_CACHE", request_id)

    reporte = await invalidar_cache(db, reporte_id)
    data = {"id": reporte.id, "estado": reporte.estado, "resultado_cache": None}

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-022", "POST", f"/api/v1/reportes/{reporte_id}/invalidar-cache", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, "Caché del reporte invalidado exitosamente")
