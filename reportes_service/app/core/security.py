"""
ms-reportes [REP] — Seguridad y generación de Request ID
REP-RF-003: Generación y Propagación de Request ID
REP-RF-001: Validación de Sesión Activa
REP-RF-002: Validación de Permisos por Funcionalidad
"""

import time
import random
import string
from fastapi import Request, HTTPException
from app.core.config import settings


# ── REP-RF-003: Generación de Request ID ──────────────────────────────────────

def generate_request_id() -> str:
    """
    Genera un identificador único con formato: REP-{timestamp_unix}-{id_corto_aleatorio}
    Ejemplo: REP-1740000000-a3f8b2
    """
    ts = int(time.time())
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"REP-{ts}-{suffix}"


def resolve_request_id(request: Request) -> str:
    """
    REP-RF-003 paso 1-3:
    - Si la petición ya trae X-Request-ID (de otro microservicio), lo reutiliza.
    - Si no, genera uno nuevo.
    """
    incoming = request.headers.get("X-Request-ID") or request.headers.get("x-request-id")
    if incoming and incoming.strip():
        return incoming.strip()
    return generate_request_id()


# ── Validación del App-Token entrante ─────────────────────────────────────────

def validate_app_token(request: Request) -> None:
    """
    Valida que la petición entrante incluya el X-App-Token correcto.
    Se usa cuando ms-reportes recibe llamadas de otros microservicios.
    """
    token = request.headers.get("X-App-Token") or request.headers.get("x-app-token")
    if not token or token != settings.APP_TOKEN_REP:
        raise HTTPException(status_code=403, detail="X-App-Token inválido o ausente")


# ── Headers salientes hacia otros microservicios ──────────────────────────────

def outgoing_headers(request_id: str, session_token: str | None = None) -> dict:
    """
    Construye los headers estándar que ms-reportes propaga a todos los
    microservicios que consume (REP-RF-003 paso 5).
    """
    headers = {
        "X-Request-ID": request_id,
        "X-App-Token": settings.APP_TOKEN_REP,
        "Content-Type": "application/json",
    }
    if session_token:
        headers["Authorization"] = f"Bearer {session_token}"
    return headers
