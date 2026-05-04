"""
ms-reportes [REP] — Cliente HTTP para microservicios externos
REP-RF-001: Validación de Sesión (ms-autenticacion)
REP-RF-002: Validación de Permisos (ms-roles)
REP-RF-012: Consultas a fuentes (ms-calificaciones, ms-inventario, ms-presupuesto)

Modo desarrollo (DEV_SKIP_AUTH=true / DEV_SKIP_SOURCES=true):
  Saltea las llamadas a microservicios externos y usa datos simulados.
  Nunca activar en producción.
"""

import logging
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import outgoing_headers

log = logging.getLogger("ms-reportes.client")


# ── Datos simulados para modo DEV_SKIP_SOURCES ───────────────────────────────

_MOCK_SOURCES: dict[str, Any] = {
    "ms-calificaciones": {
        "programas": [
            {"programa": "Ingeniería de Sistemas", "promedio": 3.85, "tasa_aprobacion": 94.2},
            {"programa": "Administración de Empresas", "promedio": 3.72, "tasa_aprobacion": 91.5},
            {"programa": "Contaduría Pública", "promedio": 3.68, "tasa_aprobacion": 89.3},
        ]
    },
    "ms-inventario": {
        "activos": [
            {"codigo": "ACT-001", "nombre": "Servidor Dell PowerEdge", "estado": "activo", "valor": 45000000},
            {"codigo": "ACT-002", "nombre": "Switch Cisco Catalyst", "estado": "activo", "valor": 8500000},
            {"codigo": "ACT-003", "nombre": "UPS APC Smart 3kVA", "estado": "mantenimiento", "valor": 3200000},
        ],
        "stock_critico": [
            {"codigo": "LAP-045", "nombre": "Laptop HP EliteBook", "stock_actual": 2, "stock_minimo": 15},
            {"codigo": "PRY-012", "nombre": "Proyector Epson 3800", "stock_actual": 1, "stock_minimo": 8},
        ]
    },
    "ms-presupuesto": {
        "areas": [
            {"area": "Vicerrectoría Académica", "asignado": 500000000, "ejecutado": 423000000, "porcentaje": 84.6},
            {"area": "Bienestar Universitario", "asignado": 120000000, "ejecutado": 98500000, "porcentaje": 82.1},
            {"area": "Sistemas", "asignado": 80000000, "ejecutado": 61000000, "porcentaje": 76.3},
        ]
    },
    # alias sin prefijo ms-
    "calificaciones": None,
    "inventario": None,
    "presupuesto": None,
}


def _mock_source(codigo: str) -> Any:
    key = codigo.lower()
    # Resolver alias
    if key == "calificaciones":
        return _MOCK_SOURCES["ms-calificaciones"]
    if key == "inventario":
        return _MOCK_SOURCES["ms-inventario"]
    if key == "presupuesto":
        return _MOCK_SOURCES["ms-presupuesto"]
    return _MOCK_SOURCES.get(key, {"mock": True, "fuente": codigo})


# ── REP-RF-001: Validar sesión con ms-autenticacion ───────────────────────────

async def validar_sesion(session_token: str, request_id: str) -> dict:
    """
    Llama a ms-autenticacion POST /api/v1/sesiones/validar.
    En DEV_SKIP_AUTH=true devuelve el usuario simulado configurado.
    """
    if settings.DEV_SKIP_AUTH:
        log.warning("[DEV] DEV_SKIP_AUTH activo — sesión simulada usuario_id=%s", settings.DEV_USER_ID)
        return {
            "sesion_valida": True,
            "usuario_id": settings.DEV_USER_ID,
            "nombre": "admin@universidad.edu",
            "rol_id": settings.DEV_ROL_ID,
            "expira_en": "2099-12-31T23:59:59Z",
        }

    url = f"{settings.MS_AUTENTICACION_URL}/api/v1/sesiones/validar"
    headers = outgoing_headers(request_id, session_token)
    payload = {"token": session_token}

    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_AUTH) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        log.error("ms-autenticacion no disponible: %s | request_id=%s", exc, request_id)
        raise HTTPException(status_code=503, detail="ms-autenticacion no disponible")

    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    if resp.status_code != 200:
        log.error("ms-autenticacion error %s | request_id=%s", resp.status_code, request_id)
        raise HTTPException(status_code=503, detail="Error al validar sesión")

    body = resp.json()
    return body.get("data", {})


# ── REP-RF-002: Verificar permisos con ms-roles ───────────────────────────────

async def verificar_permiso(rol_id: int, codigo_permiso: str, request_id: str) -> None:
    """
    Llama a ms-roles POST /api/v1/permisos/verificar.
    En DEV_SKIP_AUTH=true aprueba todo automáticamente.
    """
    if settings.DEV_SKIP_AUTH:
        log.warning("[DEV] DEV_SKIP_AUTH activo — permiso '%s' aprobado automáticamente", codigo_permiso)
        return

    url = f"{settings.MS_ROLES_URL}/api/v1/permisos/verificar"
    headers = outgoing_headers(request_id)
    payload = {"rol_id": rol_id, "codigo_permiso": codigo_permiso}

    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_AUTH) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        log.error("ms-roles no disponible: %s | request_id=%s", exc, request_id)
        raise HTTPException(status_code=503, detail="ms-roles no disponible")

    if resp.status_code == 403:
        raise HTTPException(status_code=403, detail="Sin permiso para esta operación")
    if resp.status_code != 200:
        raise HTTPException(status_code=503, detail="Error al verificar permisos")

    body = resp.json()
    if not body.get("data", {}).get("autorizado", False):
        raise HTTPException(status_code=403, detail="Sin permiso para esta operación")


# ── Helper compuesto (RF-001 + RF-002) ───────────────────────────────────────

async def autenticar_y_autorizar(
    session_token: str,
    codigo_permiso: str,
    request_id: str,
) -> dict:
    """
    Ejecuta en secuencia: validar_sesion → verificar_permiso.
    Retorna los datos del usuario autenticado.
    """
    usuario = await validar_sesion(session_token, request_id)
    rol_id = usuario.get("rol_id")
    if not rol_id:
        raise HTTPException(status_code=401, detail="No se pudo determinar el rol del usuario")
    await verificar_permiso(rol_id, codigo_permiso, request_id)
    return usuario


# ── REP-RF-012: Consultas a microservicios fuente ─────────────────────────────

async def consultar_fuente(
    base_url: str,
    endpoint: str,
    method: str,
    request_id: str,
    params: dict | None = None,
    payload: dict | None = None,
) -> Any:
    """
    Consulta genérica a un microservicio fuente.
    En DEV_SKIP_SOURCES=true devuelve datos simulados sin hacer llamada HTTP.
    """
    if settings.DEV_SKIP_SOURCES:
        # Determinar qué fuente es por la URL
        fuente = _codigo_desde_url(base_url)
        datos = _mock_source(fuente)
        log.warning("[DEV] DEV_SKIP_SOURCES activo — datos simulados para %s%s", base_url, endpoint)
        return datos

    url = f"{base_url}{endpoint}"
    headers = outgoing_headers(request_id)

    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_SOURCES) as client:
            if method.upper() == "GET":
                resp = await client.get(url, headers=headers, params=params)
            else:
                resp = await client.post(url, headers=headers, json=payload)
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        raise RuntimeError(f"Fuente {base_url} no disponible: {exc}")

    if resp.status_code != 200:
        raise RuntimeError(f"Fuente {base_url}{endpoint} retornó {resp.status_code}")

    body = resp.json()
    return body.get("data", body)


def _codigo_desde_url(url: str) -> str:
    """Deduce el código del microservicio fuente desde su URL base."""
    if "calificaciones" in url:
        return "ms-calificaciones"
    if "inventario" in url:
        return "ms-inventario"
    if "presupuesto" in url:
        return "ms-presupuesto"
    return "desconocido"


def get_source_url(codigo_microservicio: str) -> str:
    """Resuelve la URL base de un microservicio fuente por su código."""
    mapa = {
        "ms-calificaciones": settings.MS_CALIFICACIONES_URL,
        "calificaciones": settings.MS_CALIFICACIONES_URL,
        "ms-inventario": settings.MS_INVENTARIO_URL,
        "inventario": settings.MS_INVENTARIO_URL,
        "ms-presupuesto": settings.MS_PRESUPUESTO_URL,
        "presupuesto": settings.MS_PRESUPUESTO_URL,
    }
    url = mapa.get(codigo_microservicio.lower())
    if not url:
        raise ValueError(f"Microservicio fuente desconocido: {codigo_microservicio}")
    return url
