"""
ms-reportes [REP] — Router: Programaciones de Reporte
Endpoints:
  POST   /api/v1/programaciones                      → REP-RF-015
  GET    /api/v1/programaciones                      → REP-RF-016
  GET    /api/v1/programaciones/{id}                 → REP-RF-024
  PUT    /api/v1/programaciones/{id}                 → REP-RF-017
  POST   /api/v1/programaciones/{id}/desactivar      → REP-RF-018
  POST   /api/v1/programaciones/{id}/reactivar       → REP-RF-023
  POST   /api/v1/programaciones/{id}/ejecutar        → REP-RF-020
"""

import time
import logging

from fastapi import APIRouter, Depends, Request, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import resolve_request_id
from app.db.database import get_db
from app.schemas.programacion_schema import (
    ProgramacionCreate, ProgramacionUpdate, ProgramacionOut,
)
from app.services.microservice_client import autenticar_y_autorizar
from app.services.programacion_service import (
    crear_programacion, listar_programaciones, actualizar_programacion,
    desactivar_programacion, reactivar_programacion, ejecutar_manualmente,
    consultar_detalle_programacion,
)
from app.utils.logger_async import build_log_entry, send_audit_log
from app.utils.response import std_response, paginated_response

router = APIRouter(prefix="/api/v1/programaciones", tags=["Programaciones"])
log = logging.getLogger("ms-reportes.router.programaciones")


def _token(request: Request) -> str:
    return request.headers.get("Authorization", "").replace("Bearer ", "").strip()


def _serialize(obj):
    """Convierte objetos con datetime/time a JSON-safe dict."""
    import json
    from datetime import datetime, date, time
    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, time):
            return o.strftime("%H:%M:%S")
        return str(o)
    return json.loads(json.dumps(obj, default=default))


# ── POST /api/v1/programaciones ──────────────────────────────────────────────

@router.post("")
async def crear(
    request: Request,
    body: ProgramacionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-015: Crear Programación de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PROGRAMACIONES:CREAR", request_id)

    prog = await crear_programacion(db, body)
    data = ProgramacionOut.model_validate(prog).model_dump(mode="json")

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-015", "POST", "/api/v1/programaciones", 201, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, "Programación creada exitosamente", 201)


# ── GET /api/v1/programaciones ────────────────────────────────────────────────

@router.get("")
async def listar(
    request: Request,
    background_tasks: BackgroundTasks,
    estado: str | None = Query(None, description="activa | pausada"),
    plantilla_id: int | None = Query(None),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-016: Listar Programaciones de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PROGRAMACIONES:LISTAR", request_id)

    progs, total = await listar_programaciones(db, estado, plantilla_id, pagina, por_pagina)
    data = [ProgramacionOut.model_validate(p).model_dump(mode="json") for p in progs]

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-016", "GET", "/api/v1/programaciones", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return paginated_response(request_id, data, total, pagina, por_pagina, "Programaciones obtenidas exitosamente")


# ── GET /api/v1/programaciones/{id} ──────────────────────────────────────────

@router.get("/{prog_id}")
async def detalle(
    prog_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-024: Consultar Detalle de Programación"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PROGRAMACIONES:CONSULTAR", request_id)

    data = await consultar_detalle_programacion(db, prog_id)

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-024", "GET", f"/api/v1/programaciones/{prog_id}", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, _serialize(data), "Detalle de programación obtenido")


# ── PUT /api/v1/programaciones/{id} ──────────────────────────────────────────

@router.put("/{prog_id}")
async def actualizar(
    prog_id: int,
    request: Request,
    body: ProgramacionUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-017: Actualizar Programación de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PROGRAMACIONES:ACTUALIZAR", request_id)

    prog = await actualizar_programacion(db, prog_id, body)
    data = ProgramacionOut.model_validate(prog).model_dump(mode="json")

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-017", "PUT", f"/api/v1/programaciones/{prog_id}", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, data, "Programación actualizada exitosamente")


# ── POST /api/v1/programaciones/{id}/desactivar ──────────────────────────────

@router.post("/{prog_id}/desactivar")
async def desactivar(
    prog_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-018: Desactivar Programación de Reporte"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PROGRAMACIONES:DESACTIVAR", request_id)

    resultado = await desactivar_programacion(db, prog_id)

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-018", "POST", f"/api/v1/programaciones/{prog_id}/desactivar", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, resultado, "Programación desactivada exitosamente")


# ── POST /api/v1/programaciones/{id}/reactivar ───────────────────────────────

@router.post("/{prog_id}/reactivar")
async def reactivar(
    prog_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-023: Reactivar Programación Pausada"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PROGRAMACIONES:REACTIVAR", request_id)

    resultado = await reactivar_programacion(db, prog_id)

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-023", "POST", f"/api/v1/programaciones/{prog_id}/reactivar", 200, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, _serialize(resultado), "Programación reactivada exitosamente")


# ── POST /api/v1/programaciones/{id}/ejecutar ────────────────────────────────

@router.post("/{prog_id}/ejecutar")
async def ejecutar(
    prog_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """REP-RF-020: Ejecutar Manualmente Reporte Programado"""
    t0 = time.monotonic()
    request_id = resolve_request_id(request)
    usuario = await autenticar_y_autorizar(_token(request), "REP:PROGRAMACIONES:EJECUTAR_MANUAL", request_id)

    resultado = await ejecutar_manualmente(db, prog_id, usuario.get("usuario_id", 0), request_id)

    duracion = int((time.monotonic() - t0) * 1000)
    entry = build_log_entry(request_id, "REP-RF-020", "POST", f"/api/v1/programaciones/{prog_id}/ejecutar", 202, duracion, usuario.get("usuario_id"))
    background_tasks.add_task(send_audit_log, entry, request_id)

    return std_response(request_id, True, resultado, "Ejecución manual iniciada", 202)
