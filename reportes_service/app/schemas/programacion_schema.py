"""
ms-reportes [REP] — Schemas Pydantic: Programación de Reporte
REP-RF-015 a REP-RF-020, REP-RF-023, REP-RF-024
"""

from datetime import datetime, time
from typing import Any
from pydantic import BaseModel, ConfigDict


# ── Request schemas ───────────────────────────────────────────────────────────

class ProgramacionCreate(BaseModel):
    plantilla_id: int
    periodicidad: str          # diario | semanal | mensual
    dia_ejecucion: str | None = None
    hora_ejecucion: str        # "HH:MM:SS"
    destinatarios: dict[str, Any]


class ProgramacionUpdate(BaseModel):
    periodicidad: str | None = None
    dia_ejecucion: str | None = None
    hora_ejecucion: str | None = None
    destinatarios: dict[str, Any] | None = None


# ── Response schemas ──────────────────────────────────────────────────────────

class ProgramacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plantilla_id: int
    periodicidad: str
    dia_ejecucion: str | None
    hora_ejecucion: time
    destinatarios: Any
    estado: str
    ultima_ejecucion: datetime | None
    proxima_ejecucion: datetime | None
    created_at: datetime
    updated_at: datetime


class ProgramacionDetalleOut(ProgramacionOut):
    """Detalle completo con resumen de plantilla (REP-RF-024)."""
    plantilla_nombre: str | None = None
    plantilla_estado: str | None = None


class EjecucionManualOut(BaseModel):
    reporte_id: int
    programacion_id: int
    estado: str


class CambioEstadoOut(BaseModel):
    id: int
    estado_anterior: str
    estado_actual: str
    proxima_ejecucion: datetime | None = None
