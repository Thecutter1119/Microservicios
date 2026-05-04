import os
from textwrap import dedent

ROOT = r"c:\Users\jhons\Downloads\Microservicios"

SERVICES = [
    {"name": "ms-autenticacion", "code": "AUTH", "db": "db_autenticacion", "resource": "sesiones", "model": "Sesion", "table": "auth_sesiones"},
    {"name": "ms-usuarios", "code": "USR", "db": "db_usuarios", "resource": "usuarios", "model": "Usuario", "table": "usr_usuarios"},
    {"name": "ms-roles", "code": "ROL", "db": "db_roles", "resource": "roles", "model": "Rol", "table": "rol_roles"},
    {"name": "ms-inventario", "code": "INV", "db": "db_inventario", "resource": "activos", "model": "Activo", "table": "inv_activos"},
    {"name": "ms-espacios", "code": "ESP", "db": "db_espacios", "resource": "espacios", "model": "Espacio", "table": "esp_espacios"},
    {"name": "ms-reservas", "code": "RES", "db": "db_reservas", "resource": "reservas", "model": "Reserva", "table": "res_reservas"},
    {"name": "ms-presupuesto", "code": "PRE", "db": "db_presupuesto", "resource": "presupuestos", "model": "Presupuesto", "table": "pre_presupuestos"},
    {"name": "ms-gastos", "code": "GAS", "db": "db_gastos", "resource": "gastos", "model": "Gasto", "table": "gas_gastos"},
    {"name": "ms-facturacion", "code": "FAC", "db": "db_facturacion", "resource": "facturas", "model": "Factura", "table": "fac_facturas"},
    {"name": "ms-programas", "code": "PRG", "db": "db_programas", "resource": "programas", "model": "Programa", "table": "prg_programas"},
    {"name": "ms-matriculas", "code": "MAT", "db": "db_matriculas", "resource": "matriculas", "model": "Matricula", "table": "mat_matriculas"},
    {"name": "ms-calificaciones", "code": "CAL", "db": "db_calificaciones", "resource": "calificaciones", "model": "Calificacion", "table": "cal_calificaciones"},
    {"name": "ms-horarios", "code": "HOR", "db": "db_horarios", "resource": "franjas", "model": "FranjaHoraria", "table": "hor_franjas"},
    {"name": "ms-notificaciones", "code": "NOT", "db": "db_notificaciones", "resource": "notificaciones", "model": "Notificacion", "table": "not_notificaciones"},
    {"name": "ms-auditoria", "code": "AUD", "db": "db_auditoria", "resource": "eventos", "model": "EventoLog", "table": "aud_eventos"},
]

REQUIREMENTS = """fastapi==0.115.0
uvicorn==0.30.6
sqlalchemy==2.0.36
psycopg[binary]==3.2.3
pydantic==2.9.2
pydantic-settings==2.6.0
httpx==0.27.2
"""


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


for s in SERVICES:
    service_dir = os.path.join(ROOT, s["name"])
    app_dir = os.path.join(service_dir, "app")
    for d in [
        app_dir,
        os.path.join(app_dir, "api", "routes"),
        os.path.join(app_dir, "core"),
        os.path.join(app_dir, "db"),
        os.path.join(app_dir, "models"),
        os.path.join(app_dir, "schemas"),
    ]:
        os.makedirs(d, exist_ok=True)

    for pkg in [
        os.path.join(app_dir, "__init__.py"),
        os.path.join(app_dir, "api", "__init__.py"),
        os.path.join(app_dir, "api", "routes", "__init__.py"),
        os.path.join(app_dir, "core", "__init__.py"),
        os.path.join(app_dir, "db", "__init__.py"),
        os.path.join(app_dir, "models", "__init__.py"),
        os.path.join(app_dir, "schemas", "__init__.py"),
    ]:
        write(pkg, "")

    write(os.path.join(service_dir, "requirements.txt"), REQUIREMENTS)

    write(
        os.path.join(service_dir, ".env.example"),
        dedent(
            f"""\
            PROJECT_NAME={s['name']}
            SERVICE_CODE={s['code']}
            API_V1_STR=/api/v1
            DATABASE_URL=postgresql://postgres:postgres@localhost:5432/{s['db']}
            AUTH_BASE_URL=http://localhost:8001
            ROL_BASE_URL=http://localhost:8002
            AUD_BASE_URL=http://localhost:8018
            APP_TOKEN=replace-me-token-{s['code'].lower()}
            """
        ),
    )

    write(
        os.path.join(service_dir, "README.md"),
        dedent(
            f"""\
            # {s['name']}

            Microservicio base del ERP Universitario ({s['code']}) implementado con FastAPI + PostgreSQL.

            ## Ejecutar

            1. `pip install -r requirements.txt`
            2. Copiar `.env.example` a `.env`.
            3. Crear la base con `init_postgres.sql`.
            4. `uvicorn app.main:app --reload --port 80`

            ## Endpoints Base

            - `GET /health`
            - `GET /api/v1/{s['resource']}`
            - `POST /api/v1/{s['resource']}`
            - `GET /api/v1/{s['resource']}/{{id}}`
            """
        ),
    )

    write(
        os.path.join(service_dir, "init_postgres.sql"),
        dedent(
            f"""\
            CREATE DATABASE {s['db']};
            \\c {s['db']}

            CREATE TABLE IF NOT EXISTS {s['table']} (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(50) NOT NULL UNIQUE,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                estado VARCHAR(30) NOT NULL DEFAULT 'activo',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """
        ),
    )

    write(
        os.path.join(app_dir, "core", "config.py"),
        dedent(
            f"""\
            from pydantic_settings import BaseSettings, SettingsConfigDict


            class Settings(BaseSettings):
                PROJECT_NAME: str = "{s['name']}"
                SERVICE_CODE: str = "{s['code']}"
                API_V1_STR: str = "/api/v1"
                DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/{s['db']}"

                AUTH_BASE_URL: str = "http://localhost:8001"
                ROL_BASE_URL: str = "http://localhost:8002"
                AUD_BASE_URL: str = "http://localhost:8018"
                APP_TOKEN: str = "replace-me-token-{s['code'].lower()}"

                model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


            settings = Settings()
            """
        ),
    )

    write(
        os.path.join(app_dir, "core", "middleware.py"),
        dedent(
            """\
            import secrets
            import time
            from contextvars import ContextVar

            from fastapi import Request
            from starlette.middleware.base import BaseHTTPMiddleware

            from app.core.config import settings

            request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


            class RequestIdMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request: Request, call_next):
                    request_id = request.headers.get("X-Request-ID")
                    if not request_id:
                        request_id = f"{settings.SERVICE_CODE}-{int(time.time())}-{secrets.token_hex(3)}"

                    token = request_id_ctx.set(request_id)
                    response = await call_next(request)
                    response.headers["X-Request-ID"] = request_id
                    request_id_ctx.reset(token)
                    return response


            def get_current_request_id() -> str:
                return request_id_ctx.get()
            """
        ),
    )

    write(
        os.path.join(app_dir, "core", "responses.py"),
        dedent(
            """\
            from datetime import datetime, timezone
            from typing import Any, Generic, Optional, TypeVar

            from pydantic import BaseModel, Field

            from app.core.middleware import get_current_request_id

            DataT = TypeVar("DataT")


            class StandardResponse(BaseModel, Generic[DataT]):
                request_id: str = Field(default_factory=get_current_request_id)
                success: bool
                data: Optional[DataT] = None
                message: str
                timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


            def build_success_response(data: Any, message: str = "Operacion exitosa") -> StandardResponse:
                return StandardResponse(success=True, data=data, message=message)


            def build_error_response(message: str, data: Any = None) -> StandardResponse:
                return StandardResponse(success=False, data=data, message=message)
            """
        ),
    )

    write(
        os.path.join(app_dir, "db", "session.py"),
        dedent(
            """\
            from sqlalchemy import create_engine
            from sqlalchemy.orm import declarative_base, sessionmaker

            from app.core.config import settings

            engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base = declarative_base()


            def get_db():
                db = SessionLocal()
                try:
                    yield db
                finally:
                    db.close()
            """
        ),
    )

    write(
        os.path.join(app_dir, "db", "init_db.py"),
        dedent(
            """\
            from app.db.session import Base, engine
            from app.models import entities  # noqa: F401


            def init_db() -> None:
                Base.metadata.create_all(bind=engine)
            """
        ),
    )

    write(
        os.path.join(app_dir, "models", "entities.py"),
        dedent(
            f"""\
            from sqlalchemy import DateTime, Integer, String, Text, func
            from sqlalchemy.orm import Mapped, mapped_column

            from app.db.session import Base


            class {s['model']}(Base):
                __tablename__ = "{s['table']}"

                id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
                codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
                nombre: Mapped[str] = mapped_column(String(200), nullable=False)
                descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
                estado: Mapped[str] = mapped_column(String(30), default="activo")
                created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
                updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
            """
        ),
    )

    write(
        os.path.join(app_dir, "schemas", "entities.py"),
        dedent(
            """\
            from datetime import datetime

            from pydantic import BaseModel, ConfigDict


            class EntityBase(BaseModel):
                codigo: str
                nombre: str
                descripcion: str | None = None
                estado: str = "activo"


            class EntityCreate(EntityBase):
                pass


            class EntityOut(EntityBase):
                id: int
                created_at: datetime | None = None
                updated_at: datetime | None = None

                model_config = ConfigDict(from_attributes=True)
            """
        ),
    )

    write(
        os.path.join(app_dir, "api", "routes", "entities.py"),
        dedent(
            f"""\
            from fastapi import APIRouter, Depends, HTTPException
            from sqlalchemy.orm import Session

            from app.core.responses import build_success_response
            from app.db.session import get_db
            from app.models.entities import {s['model']}
            from app.schemas.entities import EntityCreate, EntityOut

            router = APIRouter(prefix="/{s['resource']}", tags=["{s['name']}"])


            @router.get("")
            def list_entities(db: Session = Depends(get_db)):
                rows = db.query({s['model']}).order_by({s['model']}.id.desc()).all()
                data = [EntityOut.model_validate(row).model_dump(mode="json") for row in rows]
                return build_success_response(data=data, message="Listado correcto")


            @router.post("")
            def create_entity(payload: EntityCreate, db: Session = Depends(get_db)):
                exists = db.query({s['model']}).filter({s['model']}.codigo == payload.codigo).first()
                if exists:
                    raise HTTPException(status_code=409, detail="El codigo ya existe")
                row = {s['model']}(**payload.model_dump())
                db.add(row)
                db.commit()
                db.refresh(row)
                return build_success_response(data=EntityOut.model_validate(row).model_dump(mode="json"), message="Creado")


            @router.get("/{{entity_id}}")
            def get_entity(entity_id: int, db: Session = Depends(get_db)):
                row = db.query({s['model']}).filter({s['model']}.id == entity_id).first()
                if not row:
                    raise HTTPException(status_code=404, detail="No encontrado")
                return build_success_response(data=EntityOut.model_validate(row).model_dump(mode="json"), message="Consulta correcta")
            """
        ),
    )

    write(
        os.path.join(app_dir, "main.py"),
        dedent(
            f"""\
            import logging
            from datetime import datetime, timezone

            from fastapi import FastAPI, Request
            from fastapi.exceptions import RequestValidationError
            from fastapi.responses import JSONResponse
            from starlette.exceptions import HTTPException as StarletteHTTPException

            from app.api.routes.entities import router as entities_router
            from app.core.config import settings
            from app.core.middleware import RequestIdMiddleware, get_current_request_id
            from app.core.responses import build_error_response, build_success_response
            from app.db.init_db import init_db

            logger = logging.getLogger(__name__)

            app = FastAPI(
                title="{s['name']}",
                description="Microservicio ERP Universitario - {s['code']}",
                version="1.0.0",
                docs_url=f"{{settings.API_V1_STR}}/docs",
                openapi_url=f"{{settings.API_V1_STR}}/openapi.json",
            )

            app.add_middleware(RequestIdMiddleware)
            app.include_router(entities_router, prefix=settings.API_V1_STR)


            @app.on_event("startup")
            def on_startup() -> None:
                init_db()


            @app.exception_handler(StarletteHTTPException)
            async def http_exception_handler(request: Request, exc: StarletteHTTPException):
                payload = build_error_response(message=str(exc.detail)).model_dump()
                payload["timestamp"] = datetime.now(timezone.utc).isoformat()
                return JSONResponse(
                    status_code=exc.status_code,
                    content=payload,
                    headers={{"X-Request-ID": get_current_request_id()}},
                )


            @app.exception_handler(RequestValidationError)
            async def validation_exception_handler(request: Request, exc: RequestValidationError):
                payload = build_error_response(
                    message="Error de validacion",
                    data={{"errors": exc.errors()}},
                ).model_dump()
                payload["timestamp"] = datetime.now(timezone.utc).isoformat()
                return JSONResponse(
                    status_code=422,
                    content=payload,
                    headers={{"X-Request-ID": get_current_request_id()}},
                )


            @app.exception_handler(Exception)
            async def global_exception_handler(request: Request, exc: Exception):
                logger.exception("Error interno no manejado")
                payload = build_error_response(message="Error interno del servidor").model_dump()
                payload["timestamp"] = datetime.now(timezone.utc).isoformat()
                return JSONResponse(
                    status_code=500,
                    content=payload,
                    headers={{"X-Request-ID": get_current_request_id()}},
                )


            @app.get("/health")
            def health_check():
                return build_success_response(
                    data={{"status": "ok", "service": settings.PROJECT_NAME}},
                    message="Servicio operativo",
                )
            """
        ),
    )

print(f"Generados {len(SERVICES)} microservicios base.")
