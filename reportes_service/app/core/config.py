"""
ms-reportes [REP] — Configuración central del microservicio
Módulo 6 — Transversales | FastAPI + Python + PostgreSQL
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Identidad del servicio ────────────────────────────────────────────────
    SERVICE_NAME: str = "ms-reportes"
    SERVICE_CODE: str = "REP"
    SERVICE_VERSION: str = "1.0.0"
    MODULE: str = "Módulo 6 — Transversales"

    # ── Base de datos ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:maicol@localhost:5432/db_reportes"
    DATABASE_URL_SYNC: str = "postgresql://postgres:maicol@localhost:5432/db_reportes"

    # ── Token de aplicación propio (X-App-Token) ──────────────────────────────
    APP_TOKEN_REP: str = "REP-APP-TOKEN-SECRET-2026"

    # ── Microservicios externos ───────────────────────────────────────────────
    MS_AUTENTICACION_URL: str = "http://autenticacion-svc:8000"
    MS_ROLES_URL: str = "http://roles-svc:8005"
    MS_CALIFICACIONES_URL: str = "http://calificaciones-svc:8001"
    MS_INVENTARIO_URL: str = "http://inventario-svc:8002"
    MS_PRESUPUESTO_URL: str = "http://presupuesto-svc:8003"
    MS_AUDITORIA_URL: str = "http://auditoria-svc:8004"

    # ── Timeouts (segundos) ───────────────────────────────────────────────────
    TIMEOUT_AUTH: int = 3
    TIMEOUT_SOURCES: int = 30
    TIMEOUT_AUDIT: int = 2

    # ── Scheduler ─────────────────────────────────────────────────────────────
    SCHEDULER_INTERVAL_MINUTES: int = 1

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["*"]

    # ── Modo desarrollo ───────────────────────────────────────────────────────
    # DEV_SKIP_AUTH=true   → saltea ms-autenticacion y ms-roles
    # DEV_SKIP_SOURCES=true → devuelve datos simulados en lugar de llamar CAL/INV/PRE
    # DEV_USER_ID=1         → usuario_id que se inyecta cuando se saltea auth
    # DEV_ROL_ID=1          → rol_id que se inyecta cuando se saltea auth
    DEV_SKIP_AUTH: bool = False
    DEV_SKIP_SOURCES: bool = False
    DEV_USER_ID: int = 1
    DEV_ROL_ID: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
