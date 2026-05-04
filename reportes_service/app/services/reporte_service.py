"""
ms-reportes [REP] — Servicio de lógica de negocio: Reportes
REP-RF-011: Solicitar Generación de Reporte (caché + async dispatch)
REP-RF-012: Generar Reporte Consolidado (proceso asíncrono)
REP-RF-013: Consultar Estado de Reporte
REP-RF-014: Descargar Reporte Generado
REP-RF-021: Listar Reportes Generados
REP-RF-022: Invalidar Caché de Reporte
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reporte import Reporte
from app.models.plantilla import Plantilla
from app.schemas.reporte_schema import ReporteCreate
from app.services.microservice_client import consultar_fuente, get_source_url
from app.utils.csv_generator import format_report
from app.utils.cache_manager import build_cache_key

log = logging.getLogger("ms-reportes.reportes")


# ── REP-RF-011: Solicitar generación ─────────────────────────────────────────

async def solicitar_reporte(
    db: AsyncSession,
    data: ReporteCreate,
    usuario_id: int,
    request_id: str,
) -> tuple[Reporte, bool]:
    """
    Lógica de caché + creación de reporte.
    Retorna (reporte, desde_cache).
    - Si existe reporte completado con mismos parámetros → HTTP 200 (caché).
    - Si no → crea registro pendiente, dispara async → HTTP 202.
    """
    # Verificar que la plantilla existe y está activa
    plantilla = await db.get(Plantilla, data.plantilla_id)
    if not plantilla:
        raise HTTPException(status_code=404, detail=f"Plantilla {data.plantilla_id} no encontrada")
    if plantilla.estado != "activa":
        raise HTTPException(status_code=422, detail="La plantilla no está activa")

    # Buscar en caché: mismo plantilla_id + parámetros + formato en estado completado
    params_json = json.dumps(dict(sorted(data.parametros.items())), sort_keys=True)
    stmt = select(Reporte).where(
        and_(
            Reporte.plantilla_id == data.plantilla_id,
            Reporte.formato_salida == data.formato_salida.upper(),
            Reporte.estado == "completado",
            Reporte.resultado_cache.isnot(None),
        )
    ).order_by(Reporte.fecha_generacion.desc()).limit(1)

    result = await db.execute(stmt)
    cached = result.scalar_one_or_none()

    if cached:
        # Verificar que los parámetros coinciden
        cached_params = json.dumps(dict(sorted((cached.parametros or {}).items())), sort_keys=True)
        if cached_params == params_json:
            log.info("Reporte desde caché id=%s request_id=%s", cached.id, request_id)
            return cached, True

    # No hay caché: crear nuevo reporte en estado pendiente
    reporte = Reporte(
        plantilla_id=data.plantilla_id,
        nombre=data.nombre,
        parametros=data.parametros,
        formato_salida=data.formato_salida.upper(),
        estado="pendiente",
        solicitado_por=usuario_id,
        fecha_solicitud=datetime.utcnow(),
    )
    db.add(reporte)
    await db.flush()
    await db.refresh(reporte)

    # Disparar generación asíncrona (REP-RF-012) en background
    reporte_id = reporte.id
    asyncio.create_task(
        _generar_reporte_async(reporte_id, plantilla, data.parametros, data.formato_salida.upper(), request_id)
    )

    log.info("Reporte creado id=%s estado=pendiente request_id=%s", reporte_id, request_id)
    return reporte, False


# ── REP-RF-012: Proceso asíncrono de generación ───────────────────────────────

async def _generar_reporte_async(
    reporte_id: int,
    plantilla: Plantilla,
    parametros: dict,
    formato: str,
    request_id: str,
) -> None:
    """
    Proceso asíncrono de consolidación de datos.
    Se ejecuta en background tras retornar 202 al usuario.
    Flujo: pendiente → generando → completado | error
    """
    from app.db.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Cambiar a estado generando
            reporte = await db.get(Reporte, reporte_id)
            if not reporte:
                return
            reporte.estado = "generando"
            await db.commit()

            # Consultar cada microservicio fuente según configuracion_consultas
            config = plantilla.configuracion_consultas or {}
            fuentes = plantilla.microservicios_fuente or []
            datos_consolidados = {}

            for fuente_codigo in fuentes:
                fuente_config = config.get(fuente_codigo, {})
                if not fuente_config:
                    continue
                base_url = get_source_url(fuente_codigo)
                endpoint = fuente_config.get("endpoint", "/reportes")
                method = fuente_config.get("method", "GET")

                try:
                    datos = await consultar_fuente(
                        base_url=base_url,
                        endpoint=endpoint,
                        method=method,
                        request_id=request_id,
                        params=parametros if method == "GET" else None,
                        payload=parametros if method != "GET" else None,
                    )
                    datos_consolidados[fuente_codigo] = datos
                except RuntimeError as exc:
                    log.error("Error consultando fuente %s: %s | reporte_id=%s", fuente_codigo, exc, reporte_id)
                    datos_consolidados[fuente_codigo] = {"error": str(exc)}

            # Formatear resultado
            contenido, _, _ = format_report(datos_consolidados, formato)
            tamano = len(contenido.encode("utf-8"))

            # Actualizar reporte a completado
            reporte = await db.get(Reporte, reporte_id)
            reporte.estado = "completado"
            reporte.resultado_cache = contenido
            reporte.fecha_generacion = datetime.utcnow()
            reporte.tamano_bytes = tamano
            await db.commit()
            log.info("Reporte completado id=%s tamano_bytes=%s", reporte_id, tamano)

        except Exception as exc:
            log.error("Error en generación reporte id=%s: %s", reporte_id, exc)
            try:
                async with AsyncSessionLocal() as db2:
                    r = await db2.get(Reporte, reporte_id)
                    if r:
                        r.estado = "error"
                        r.fecha_generacion = datetime.utcnow()
                        await db2.commit()
            except Exception:
                pass


# ── REP-RF-013: Consultar estado ──────────────────────────────────────────────

async def consultar_estado_reporte(db: AsyncSession, reporte_id: int) -> Reporte:
    """Retorna metadatos del reporte SIN resultado_cache."""
    reporte = await db.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail=f"Reporte {reporte_id} no encontrado")
    return reporte


# ── REP-RF-014: Descargar reporte ─────────────────────────────────────────────

async def descargar_reporte(db: AsyncSession, reporte_id: int) -> tuple[Reporte, str]:
    """
    Retorna el reporte y su contenido para descarga.
    Solo aplica a reportes en estado completado.
    """
    reporte = await db.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail=f"Reporte {reporte_id} no encontrado")
    if reporte.estado != "completado":
        raise HTTPException(
            status_code=422,
            detail=f"El reporte está en estado '{reporte.estado}'. Solo se pueden descargar reportes completados."
        )
    if not reporte.resultado_cache:
        raise HTTPException(status_code=422, detail="El reporte no tiene contenido en caché")
    return reporte, reporte.resultado_cache


# ── REP-RF-021: Listar reportes generados ────────────────────────────────────

async def listar_reportes(
    db: AsyncSession,
    estado: str | None = None,
    plantilla_id: int | None = None,
    solicitado_por: int | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> tuple[list[Reporte], int]:
    """Lista reportes SIN resultado_cache. REP-RF-021."""
    conditions = []
    if estado:
        conditions.append(Reporte.estado == estado)
    if plantilla_id:
        conditions.append(Reporte.plantilla_id == plantilla_id)
    if solicitado_por:
        conditions.append(Reporte.solicitado_por == solicitado_por)
    if fecha_desde:
        conditions.append(Reporte.fecha_solicitud >= fecha_desde)
    if fecha_hasta:
        conditions.append(Reporte.fecha_solicitud <= fecha_hasta)

    query = select(Reporte)
    count_q = select(func.count()).select_from(Reporte)
    if conditions:
        query = query.where(and_(*conditions))
        count_q = count_q.where(and_(*conditions))

    query = query.order_by(Reporte.created_at.desc())
    query = query.offset((pagina - 1) * por_pagina).limit(por_pagina)

    result = await db.execute(query)
    reportes = result.scalars().all()
    total = await db.scalar(count_q)
    return list(reportes), total or 0


# ── REP-RF-022: Invalidar caché ──────────────────────────────────────────────

async def invalidar_cache(db: AsyncSession, reporte_id: int) -> Reporte:
    """
    Limpia resultado_cache y vuelve el reporte a estado pendiente.
    Solo aplica a reportes completados.
    """
    reporte = await db.get(Reporte, reporte_id)
    if not reporte:
        raise HTTPException(status_code=404, detail=f"Reporte {reporte_id} no encontrado")
    if reporte.estado != "completado":
        raise HTTPException(
            status_code=422,
            detail=f"Solo se puede invalidar caché de reportes completados. Estado actual: '{reporte.estado}'"
        )
    reporte.resultado_cache = None
    reporte.estado = "pendiente"
    await db.flush()
    await db.refresh(reporte)
    log.info("Caché invalidado reporte_id=%s", reporte_id)
    return reporte
