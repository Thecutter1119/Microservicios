"""
ms-reportes [REP] — Schemas Pydantic: Plantilla de Reporte
REP-RF-005: Estructura de Respuesta Estándar
REP-RF-006 a REP-RF-010
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


# ── Request schemas ───────────────────────────────────────────────────────────

class PlantillaCreate(BaseModel):
    nombre: str
    descripcion: str
    microservicios_fuente: list[str]
    parametros_requeridos: list[dict[str, Any]]
    configuracion_consultas: dict[str, Any]
    estado: str = "activa"


class PlantillaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    microservicios_fuente: list[str] | None = None
    parametros_requeridos: list[dict[str, Any]] | None = None
    configuracion_consultas: dict[str, Any] | None = None
    estado: str | None = None


# ── Response schemas ──────────────────────────────────────────────────────────

class PlantillaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str
    microservicios_fuente: Any
    parametros_requeridos: Any
    configuracion_consultas: Any
    estado: str
    created_at: datetime
    updated_at: datetime


class PlantillaResumen(BaseModel):
    """Resumen ligero para embeber en otras respuestas."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    estado: str


# ── Estructura de respuesta estándar (REP-RF-005) ─────────────────────────────

class PaginacionMeta(BaseModel):
    pagina: int
    por_pagina: int
    total: int
    paginas: int


class RespuestaEstandar(BaseModel):
    request_id: str
    success: bool
    data: Any
    message: str
    timestamp: datetime


class RespuestaPaginada(BaseModel):
    request_id: str
    success: bool
    data: list[Any]
    paginacion: PaginacionMeta
    message: str
    timestamp: datetime
