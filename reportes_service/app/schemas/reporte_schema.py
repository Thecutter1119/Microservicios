"""
ms-reportes [REP] — Schemas Pydantic: Reporte
REP-RF-011 a REP-RF-014, REP-RF-021, REP-RF-022
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


# ── Request schemas ───────────────────────────────────────────────────────────

class ReporteCreate(BaseModel):
    plantilla_id: int
    nombre: str
    parametros: dict[str, Any]
    formato_salida: str = "CSV"   # CSV | JSON


# ── Response schemas ──────────────────────────────────────────────────────────

class ReporteOut(BaseModel):
    """Respuesta sin resultado_cache (para listados y consultas de estado)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    plantilla_id: int
    nombre: str
    parametros: Any
    formato_salida: str
    estado: str
    solicitado_por: int
    fecha_solicitud: datetime
    fecha_generacion: datetime | None
    tamano_bytes: int | None
    created_at: datetime


class ReporteSolicitudOut(BaseModel):
    """Respuesta inmediata tras solicitar generación (202 o 200 caché)."""
    reporte_id: int
    estado: str
    desde_cache: bool = False
