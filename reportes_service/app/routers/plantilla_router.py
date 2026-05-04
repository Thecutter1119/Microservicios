"""
ms-reportes [REP] — Router: Plantillas de Reporte
Endpoints:
  POST   /api/v1/plantillas           → REP-RF-006
  GET    /api/v1/plantillas           → REP-RF-008
  GET    /api/v1/plantillas/{id}      → REP-RF-007
  PUT    /api/v1/plantillas/{id}      → REP-RF-009
  DELETE /api/v1/plantillas/{id}      → REP-RF-010
"""

import time
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import resolve_request_id
from app.db.database import get_db
from app.schemas.plantilla_schema import PlantillaCreate, PlantillaUpdate, PlantillaOut
from app.services.microservice_client import autenticar_y_autorizar
from app.services.plantilla_service import (
    crear_plantilla, obtener_plantilla, listar_plantillas,
    actualizar_plantilla, eliminar_plantilla,
)
from app.utils.logger_async import build_log_entry, send_audit_log
from app.utils.response import std_response, paginated_response

router = APIRouter(prefix="/api/v1/plantillas", tags=["Plantillas"])
log = logging.getLogger("ms-reportes.router.plantillas")


def _token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    return auth.replace("Bearer ", "").strip()


# ── POST /api/v1/plantillas ───────────────────────────────────────────────────

@router.post("")
async def crear(
    request: Request,
    body: PlantillaCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-006: Crear Plantilla de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PLANTILLAS:CREAR", request_id)

    plantilla = await crear_plantilla(db, body)
    data = PlantillaOut.model_validate(plantilla).model_dump(mode="json")

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-006", "POST", "/api/v1/plantillas", 201, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, "Plantilla creada exitosamente", 201)


# ── GET /api/v1/plantillas ────────────────────────────────────────────────────

@router.get("")
async def listar(
    request: Request,
    background_tasks: BackgroundTasks,
    estado: str | None = Query(None, description="activa | inactiva"),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-008: Listar Plantillas de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PLANTILLAS:LISTAR", request_id)

    plantillas, total = await listar_plantillas(db, estado, pagina, por_pagina)
    data = [PlantillaOut.model_validate(p).model_dump(mode="json") for p in plantillas]

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-008", "GET", "/api/v1/plantillas", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return paginated_response(request_id, data, total, pagina, por_pagina, "Plantillas obtenidas exitosamente")


# ── GET /api/v1/plantillas/{id} ───────────────────────────────────────────────

@router.get("/{plantilla_id}")
async def consultar(
    plantilla_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-007: Consultar Plantilla de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PLANTILLAS:CONSULTAR", request_id)

    plantilla = await obtener_plantilla(db, plantilla_id)
    data = PlantillaOut.model_validate(plantilla).model_dump(mode="json")

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-007", "GET", f"/api/v1/plantillas/{plantilla_id}", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, "Plantilla obtenida exitosamente")


# ── PUT /api/v1/plantillas/{id} ───────────────────────────────────────────────

@router.put("/{plantilla_id}")
async def actualizar(
    plantilla_id: int,
    request: Request,
    body: PlantillaUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-009: Actualizar Plantilla de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PLANTILLAS:ACTUALIZAR", request_id)

    plantilla = await actualizar_plantilla(db, plantilla_id, body)
    data = PlantillaOut.model_validate(plantilla).model_dump(mode="json")

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-009", "PUT", f"/api/v1/plantillas/{plantilla_id}", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, "Plantilla actualizada exitosamente")


# ── DELETE /api/v1/plantillas/{id} ───────────────────────────────────────────

@router.delete("/{plantilla_id}")
async def eliminar(
    plantilla_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-010: Eliminar Plantilla de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PLANTILLAS:ELIMINAR", request_id)

    resultado = await eliminar_plantilla(db, plantilla_id)

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-010", "DELETE", f"/api/v1/plantillas/{plantilla_id}", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, resultado, "Plantilla eliminada exitosamente")
