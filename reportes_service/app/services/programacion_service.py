"""
ms-reportes [REP] — Servicio de lógica de negocio: Programaciones
REP-RF-015: Crear Programación
REP-RF-016: Listar Programaciones
REP-RF-017: Actualizar Programación
REP-RF-018: Desactivar Programación
REP-RF-019: Ejecutar Automáticamente (scheduler interno)
REP-RF-020: Ejecutar Manualmente
REP-RF-023: Reactivar Programación Pausada
REP-RF-024: Consultar Detalle de Programación
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.programacion import Programacion
from app.models.reporte import Reporte
from app.models.plantilla import Plantilla
from app.schemas.programacion_schema import ProgramacionCreate, ProgramacionUpdate

log = logging.getLogger("ms-reportes.programaciones")


# ── Cálculo de próxima ejecución ──────────────────────────────────────────────

def calcular_proxima_ejecucion(
    periodicidad: str,
    dia_ejecucion: str | None,
    hora_ejecucion_str: str,
    desde: datetime | None = None,
) -> datetime:
    """
    Calcula la próxima fecha/hora de ejecución desde `desde` (default: now UTC).
    Lógica:
    - diario:   siguiente ocurrencia de hora_ejecucion
    - semanal:  siguiente ocurrencia de dia_ejecucion + hora_ejecucion
    - mensual:  siguiente ocurrencia de dia_ejecucion (int) + hora_ejecucion
    """
    now = desde or datetime.utcnow()
    # Parsear hora
    partes = hora_ejecucion_str.split(":")
    hora = int(partes[0])
    minuto = int(partes[1]) if len(partes) > 1 else 0
    segundo = int(partes[2]) if len(partes) > 2 else 0

    if periodicidad == "diario":
        candidato = now.replace(hour=hora, minute=minuto, second=segundo, microsecond=0)
        if candidato <= now:
            candidato += timedelta(days=1)
        return candidato

    elif periodicidad == "semanal":
        dias_semana = {
            "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
            "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6
        }
        dia_target = dias_semana.get((dia_ejecucion or "lunes").lower(), 0)
        dias_hasta = (dia_target - now.weekday()) % 7
        if dias_hasta == 0:
            candidato = now.replace(hour=hora, minute=minuto, second=segundo, microsecond=0)
            if candidato <= now:
                dias_hasta = 7
        candidato = (now + timedelta(days=dias_hasta)).replace(
            hour=hora, minute=minuto, second=segundo, microsecond=0
        )
        return candidato

    else:  # mensual
        dia_num = int(dia_ejecucion or "1")
        # Intentar este mes
        try:
            candidato = now.replace(day=dia_num, hour=hora, minute=minuto, second=segundo, microsecond=0)
        except ValueError:
            # Día no válido en este mes (ej: 31 en febrero)
            candidato = None

        if candidato is None or candidato <= now:
            # Siguiente mes
            if now.month == 12:
                siguiente = now.replace(year=now.year + 1, month=1)
            else:
                siguiente = now.replace(month=now.month + 1)
            try:
                candidato = siguiente.replace(day=dia_num, hour=hora, minute=minuto, second=segundo, microsecond=0)
            except ValueError:
                candidato = siguiente.replace(day=28, hour=hora, minute=minuto, second=segundo, microsecond=0)
        return candidato


# ── REP-RF-015: Crear programación ───────────────────────────────────────────

async def crear_programacion(db: AsyncSession, data: ProgramacionCreate) -> Programacion:
    """Crea una nueva programación y calcula proxima_ejecucion."""
    plantilla = await db.get(Plantilla, data.plantilla_id)
    if not plantilla:
        raise HTTPException(status_code=404, detail=f"Plantilla {data.plantilla_id} no encontrada")

    proxima = calcular_proxima_ejecucion(
        data.periodicidad, data.dia_ejecucion, data.hora_ejecucion
    )
    from datetime import time as dtime
    partes = data.hora_ejecucion.split(":")
    hora_obj = dtime(int(partes[0]), int(partes[1]) if len(partes) > 1 else 0)

    prog = Programacion(
        plantilla_id=data.plantilla_id,
        periodicidad=data.periodicidad,
        dia_ejecucion=data.dia_ejecucion,
        hora_ejecucion=hora_obj,
        destinatarios=data.destinatarios,
        estado="activa",
        proxima_ejecucion=proxima,
    )
    db.add(prog)
    await db.flush()
    await db.refresh(prog)
    log.info("Programación creada id=%s plantilla_id=%s proxima=%s", prog.id, prog.plantilla_id, proxima)
    return prog


# ── REP-RF-016: Listar programaciones ────────────────────────────────────────

async def listar_programaciones(
    db: AsyncSession,
    estado: str | None = None,
    plantilla_id: int | None = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> tuple[list[Programacion], int]:
    conditions = []
    if estado:
        conditions.append(Programacion.estado == estado)
    if plantilla_id:
        conditions.append(Programacion.plantilla_id == plantilla_id)

    query = select(Programacion)
    count_q = select(func.count()).select_from(Programacion)
    if conditions:
        query = query.where(and_(*conditions))
        count_q = count_q.where(and_(*conditions))

    query = query.order_by(Programacion.created_at.desc())
    query = query.offset((pagina - 1) * por_pagina).limit(por_pagina)

    result = await db.execute(query)
    progs = result.scalars().all()
    total = await db.scalar(count_q)
    return list(progs), total or 0


# ── REP-RF-017: Actualizar programación ──────────────────────────────────────

async def actualizar_programacion(
    db: AsyncSession, prog_id: int, data: ProgramacionUpdate
) -> Programacion:
    """Actualiza campos. Recalcula proxima_ejecucion si cambia periodicidad/día/hora."""
    prog = await db.get(Programacion, prog_id)
    if not prog:
        raise HTTPException(status_code=404, detail=f"Programación {prog_id} no encontrada")

    recalcular = False
    if data.periodicidad is not None and data.periodicidad != prog.periodicidad:
        prog.periodicidad = data.periodicidad
        recalcular = True
    if data.dia_ejecucion is not None and data.dia_ejecucion != prog.dia_ejecucion:
        prog.dia_ejecucion = data.dia_ejecucion
        recalcular = True
    if data.hora_ejecucion is not None:
        from datetime import time as dtime
        partes = data.hora_ejecucion.split(":")
        nueva_hora = dtime(int(partes[0]), int(partes[1]) if len(partes) > 1 else 0)
        if nueva_hora != prog.hora_ejecucion:
            prog.hora_ejecucion = nueva_hora
            recalcular = True
    if data.destinatarios is not None:
        prog.destinatarios = data.destinatarios

    if recalcular:
        hora_str = prog.hora_ejecucion.strftime("%H:%M:%S")
        prog.proxima_ejecucion = calcular_proxima_ejecucion(
            prog.periodicidad, prog.dia_ejecucion, hora_str
        )

    prog.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(prog)
    return prog


# ── REP-RF-018: Desactivar programación ──────────────────────────────────────

async def desactivar_programacion(db: AsyncSession, prog_id: int) -> dict:
    prog = await db.get(Programacion, prog_id)
    if not prog:
        raise HTTPException(status_code=404, detail=f"Programación {prog_id} no encontrada")
    if prog.estado == "pausada":
        raise HTTPException(status_code=422, detail="La programación ya está pausada")

    estado_anterior = prog.estado
    prog.estado = "pausada"
    prog.updated_at = datetime.utcnow()
    await db.flush()
    return {"id": prog_id, "estado_anterior": estado_anterior, "estado_actual": "pausada"}


# ── REP-RF-023: Reactivar programación ───────────────────────────────────────

async def reactivar_programacion(db: AsyncSession, prog_id: int) -> dict:
    prog = await db.get(Programacion, prog_id)
    if not prog:
        raise HTTPException(status_code=404, detail=f"Programación {prog_id} no encontrada")
    if prog.estado == "activa":
        raise HTTPException(status_code=422, detail="La programación ya está activa")

    hora_str = prog.hora_ejecucion.strftime("%H:%M:%S")
    nueva_proxima = calcular_proxima_ejecucion(
        prog.periodicidad, prog.dia_ejecucion, hora_str
    )
    prog.estado = "activa"
    prog.proxima_ejecucion = nueva_proxima
    prog.updated_at = datetime.utcnow()
    await db.flush()
    return {
        "id": prog_id,
        "estado_anterior": "pausada",
        "estado_actual": "activa",
        "proxima_ejecucion": nueva_proxima,
    }


# ── REP-RF-020: Ejecutar manualmente ─────────────────────────────────────────

async def ejecutar_manualmente(
    db: AsyncSession, prog_id: int, usuario_id: int, request_id: str
) -> dict:
    """
    Crea reporte en pendiente y dispara generación async.
    No modifica proxima_ejecucion. Acepta activa y pausada.
    """
    prog = await db.get(Programacion, prog_id)
    if not prog:
        raise HTTPException(status_code=404, detail=f"Programación {prog_id} no encontrada")

    plantilla = await db.get(Plantilla, prog.plantilla_id)
    if not plantilla:
        raise HTTPException(status_code=404, detail="Plantilla de la programación no encontrada")

    reporte = Reporte(
        plantilla_id=prog.plantilla_id,
        nombre=f"{plantilla.nombre} — Ejecución manual {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        parametros={},
        formato_salida="CSV",
        estado="pendiente",
        solicitado_por=usuario_id,
        fecha_solicitud=datetime.utcnow(),
    )
    db.add(reporte)
    prog.ultima_ejecucion = datetime.utcnow()
    prog.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(reporte)

    # Disparar generación asíncrona
    from app.services.reporte_service import _generar_reporte_async
    asyncio.create_task(
        _generar_reporte_async(reporte.id, plantilla, {}, "CSV", request_id)
    )

    log.info("Ejecución manual prog_id=%s reporte_id=%s", prog_id, reporte.id)
    return {"reporte_id": reporte.id, "programacion_id": prog_id, "estado": "pendiente"}


# ── REP-RF-024: Consultar detalle de programación ────────────────────────────

async def consultar_detalle_programacion(db: AsyncSession, prog_id: int) -> dict:
    prog = await db.get(Programacion, prog_id)
    if not prog:
        raise HTTPException(status_code=404, detail=f"Programación {prog_id} no encontrada")

    plantilla = await db.get(Plantilla, prog.plantilla_id)
    result = {
        "id": prog.id,
        "plantilla_id": prog.plantilla_id,
        "plantilla_nombre": plantilla.nombre if plantilla else None,
        "plantilla_estado": plantilla.estado if plantilla else None,
        "periodicidad": prog.periodicidad,
        "dia_ejecucion": prog.dia_ejecucion,
        "hora_ejecucion": str(prog.hora_ejecucion),
        "destinatarios": prog.destinatarios,
        "estado": prog.estado,
        "ultima_ejecucion": prog.ultima_ejecucion,
        "proxima_ejecucion": prog.proxima_ejecucion,
        "created_at": prog.created_at,
        "updated_at": prog.updated_at,
    }
    return result


# ── REP-RF-019: Scheduler interno ────────────────────────────────────────────

async def ejecutar_programaciones_vencidas() -> None:
    """
    Proceso interno del scheduler (no HTTP).
    Evalúa programaciones activas cuya proxima_ejecucion <= now().
    Crea reportes pendientes y recalcula proxima_ejecucion.
    """
    from app.db.database import AsyncSessionLocal
    from app.services.reporte_service import _generar_reporte_async

    # Usar datetime naive (sin timezone) para comparar con TIMESTAMP WITHOUT TIME ZONE de PostgreSQL
    now = datetime.utcnow()
    log.debug("Scheduler: evaluando programaciones vencidas a %s", now.isoformat())

    async with AsyncSessionLocal() as db:
        try:
            stmt = select(Programacion).where(
                and_(
                    Programacion.estado == "activa",
                    Programacion.proxima_ejecucion <= now,
                )
            )
            result = await db.execute(stmt)
            pendientes = result.scalars().all()

            for prog in pendientes:
                plantilla = await db.get(Plantilla, prog.plantilla_id)
                if not plantilla or plantilla.estado != "activa":
                    continue

                reporte = Reporte(
                    plantilla_id=prog.plantilla_id,
                    nombre=f"{plantilla.nombre} — Auto {now.strftime('%Y-%m-%d %H:%M')}",
                    parametros={},
                    formato_salida="CSV",
                    estado="pendiente",
                    solicitado_por=0,  # sistema
                    fecha_solicitud=now,
                )
                db.add(reporte)
                prog.ultima_ejecucion = now
                hora_str = prog.hora_ejecucion.strftime("%H:%M:%S")
                prog.proxima_ejecucion = calcular_proxima_ejecucion(
                    prog.periodicidad, prog.dia_ejecucion, hora_str, desde=now
                )
                prog.updated_at = now

            await db.commit()

            # Disparar generación async para cada reporte creado
            for prog in pendientes:
                plantilla = await db.get(Plantilla, prog.plantilla_id)
                if plantilla:
                    stmt2 = select(Reporte).where(
                        and_(Reporte.plantilla_id == prog.plantilla_id, Reporte.estado == "pendiente")
                    ).order_by(Reporte.created_at.desc()).limit(1)
                    r = await db.scalar(stmt2)
                    if r:
                        asyncio.create_task(
                            _generar_reporte_async(r.id, plantilla, {}, "CSV", f"SCHEDULER-{r.id}")
                        )

            if pendientes:
                log.info("Scheduler: %d programaciones ejecutadas", len(pendientes))

        except Exception as exc:
            log.error("Error en scheduler: %s", exc)
