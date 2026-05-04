"""
ms-reportes [REP] — Servicio de lógica de negocio: Plantillas de Reporte
REP-RF-006: Crear Plantilla
REP-RF-007: Consultar Plantilla
REP-RF-008: Listar Plantillas
REP-RF-009: Actualizar Plantilla
REP-RF-010: Eliminar Plantilla
"""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plantilla import Plantilla
from app.models.reporte import Reporte
from app.models.programacion import Programacion
from app.schemas.plantilla_schema import PlantillaCreate, PlantillaUpdate

log = logging.getLogger("ms-reportes.plantillas")


async def crear_plantilla(db: AsyncSession, data: PlantillaCreate) -> Plantilla:
    """REP-RF-006: Crea una nueva plantilla. Valida unicidad del nombre."""
    # Verificar unicidad del nombre
    existe = await db.scalar(select(Plantilla).where(Plantilla.nombre == data.nombre))
    if existe:
        raise HTTPException(status_code=409, detail=f"Ya existe una plantilla con el nombre '{data.nombre}'")

    plantilla = Plantilla(
        nombre=data.nombre,
        descripcion=data.descripcion,
        microservicios_fuente=data.microservicios_fuente,
        parametros_requeridos=data.parametros_requeridos,
        configuracion_consultas=data.configuracion_consultas,
        estado=data.estado,
    )
    db.add(plantilla)
    await db.flush()
    await db.refresh(plantilla)
    log.info("Plantilla creada id=%s nombre=%s", plantilla.id, plantilla.nombre)
    return plantilla


async def obtener_plantilla(db: AsyncSession, plantilla_id: int) -> Plantilla:
    """REP-RF-007: Consulta el detalle completo de una plantilla por ID."""
    plantilla = await db.get(Plantilla, plantilla_id)
    if not plantilla:
        raise HTTPException(status_code=404, detail=f"Plantilla {plantilla_id} no encontrada")
    return plantilla


async def listar_plantillas(
    db: AsyncSession,
    estado: str | None = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> tuple[list[Plantilla], int]:
    """REP-RF-008: Lista plantillas con filtro opcional por estado y paginación."""
    query = select(Plantilla)
    count_query = select(func.count()).select_from(Plantilla)

    if estado:
        query = query.where(Plantilla.estado == estado)
        count_query = count_query.where(Plantilla.estado == estado)

    query = query.order_by(Plantilla.created_at.desc())
    query = query.offset((pagina - 1) * por_pagina).limit(por_pagina)

    result = await db.execute(query)
    plantillas = result.scalars().all()
    total = await db.scalar(count_query)
    return list(plantillas), total or 0


async def actualizar_plantilla(db: AsyncSession, plantilla_id: int, data: PlantillaUpdate) -> Plantilla:
    """
    REP-RF-009: Actualiza campos de una plantilla.
    Si se cambia el nombre, verifica unicidad.
    """
    plantilla = await obtener_plantilla(db, plantilla_id)

    if data.nombre and data.nombre != plantilla.nombre:
        existe = await db.scalar(select(Plantilla).where(Plantilla.nombre == data.nombre))
        if existe:
            raise HTTPException(status_code=409, detail=f"Ya existe una plantilla con el nombre '{data.nombre}'")
        plantilla.nombre = data.nombre

    if data.descripcion is not None:
        plantilla.descripcion = data.descripcion
    if data.microservicios_fuente is not None:
        plantilla.microservicios_fuente = data.microservicios_fuente
    if data.parametros_requeridos is not None:
        plantilla.parametros_requeridos = data.parametros_requeridos
    if data.configuracion_consultas is not None:
        plantilla.configuracion_consultas = data.configuracion_consultas
    if data.estado is not None:
        plantilla.estado = data.estado

    plantilla.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(plantilla)
    return plantilla


async def eliminar_plantilla(db: AsyncSession, plantilla_id: int) -> dict:
    """
    REP-RF-010: Elimina una plantilla.
    Verifica que no tenga programaciones activas ni reportes en proceso.
    """
    plantilla = await obtener_plantilla(db, plantilla_id)

    # Verificar programaciones activas
    prog_activas = await db.scalar(
        select(func.count()).select_from(Programacion)
        .where(Programacion.plantilla_id == plantilla_id, Programacion.estado == "activa")
    )
    if prog_activas:
        raise HTTPException(
            status_code=409,
            detail=f"No se puede eliminar: la plantilla tiene {prog_activas} programación(es) activa(s)"
        )

    # Verificar reportes en proceso
    reportes_en_proceso = await db.scalar(
        select(func.count()).select_from(Reporte)
        .where(
            Reporte.plantilla_id == plantilla_id,
            or_(Reporte.estado == "pendiente", Reporte.estado == "generando")
        )
    )
    if reportes_en_proceso:
        raise HTTPException(
            status_code=409,
            detail=f"No se puede eliminar: hay {reportes_en_proceso} reporte(s) en proceso"
        )

    nombre = plantilla.nombre
    await db.delete(plantilla)
    await db.flush()
    log.info("Plantilla eliminada id=%s nombre=%s", plantilla_id, nombre)
    return {"id": plantilla_id, "nombre": nombre, "eliminada": True}
