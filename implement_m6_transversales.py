from pathlib import Path
from textwrap import dedent

ROOT = Path(r"c:\Users\jhons\Downloads\Microservicios")


def write(rel_path: str, content: str) -> None:
    file_path = ROOT / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


COMMON_REQ = dedent(
    """\
    fastapi==0.115.0
    uvicorn==0.30.6
    sqlalchemy==2.0.36
    psycopg[binary]==3.2.3
    pydantic==2.9.2
    pydantic-settings==2.6.0
    """
)

# ms-notificaciones
write("ms-notificaciones/requirements.txt", COMMON_REQ)
write(
    "ms-notificaciones/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-notificaciones
        SERVICE_CODE=NOT
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_notificaciones
        """
    ),
)
write(
    "ms-notificaciones/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_notificaciones;
        \\c db_notificaciones

        CREATE TABLE IF NOT EXISTS not_notificaciones (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            canal VARCHAR(20) NOT NULL,
            asunto VARCHAR(180),
            mensaje TEXT NOT NULL,
            prioridad VARCHAR(20) NOT NULL DEFAULT 'normal',
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            intentos INTEGER NOT NULL DEFAULT 0,
            max_intentos INTEGER NOT NULL DEFAULT 3,
            request_id VARCHAR(80),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_envio TIMESTAMP,
            fecha_lectura TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS not_plantillas (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL UNIQUE,
            canal VARCHAR(20) NOT NULL,
            asunto_template TEXT,
            mensaje_template TEXT NOT NULL,
            variables_requeridas TEXT,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS not_preferencias_usuario (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL UNIQUE,
            canal_preferido VARCHAR(20) NOT NULL,
            notificaciones_activas BOOLEAN NOT NULL DEFAULT TRUE,
            no_molestar_inicio TIME,
            no_molestar_fin TIME
        );

        CREATE TABLE IF NOT EXISTS not_historial_reintentos (
            id SERIAL PRIMARY KEY,
            notificacion_id INTEGER NOT NULL REFERENCES not_notificaciones(id),
            numero_intento INTEGER NOT NULL,
            resultado VARCHAR(20) NOT NULL,
            detalle_error TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-notificaciones/app/models/entities.py",
    dedent(
        """\
        from datetime import datetime
        from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Time, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class Notificacion(Base):
            __tablename__ = "not_notificaciones"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            canal: Mapped[str] = mapped_column(String(20), nullable=False)
            asunto: Mapped[str | None] = mapped_column(String(180), nullable=True)
            mensaje: Mapped[str] = mapped_column(Text, nullable=False)
            prioridad: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
            intentos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            max_intentos: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
            request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            fecha_envio: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            fecha_lectura: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Plantilla(Base):
            __tablename__ = "not_plantillas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
            canal: Mapped[str] = mapped_column(String(20), nullable=False)
            asunto_template: Mapped[str | None] = mapped_column(Text, nullable=True)
            mensaje_template: Mapped[str] = mapped_column(Text, nullable=False)
            variables_requeridas: Mapped[str | None] = mapped_column(Text, nullable=True)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class PreferenciaUsuario(Base):
            __tablename__ = "not_preferencias_usuario"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            usuario_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
            canal_preferido: Mapped[str] = mapped_column(String(20), nullable=False)
            notificaciones_activas: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
            no_molestar_inicio: Mapped[str | None] = mapped_column(Time, nullable=True)
            no_molestar_fin: Mapped[str | None] = mapped_column(Time, nullable=True)


        class HistorialReintento(Base):
            __tablename__ = "not_historial_reintentos"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            notificacion_id: Mapped[int] = mapped_column(ForeignKey("not_notificaciones.id"), nullable=False, index=True)
            numero_intento: Mapped[int] = mapped_column(Integer, nullable=False)
            resultado: Mapped[str] = mapped_column(String(20), nullable=False)
            detalle_error: Mapped[str | None] = mapped_column(Text, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
        """
    ),
)
write(
    "ms-notificaciones/app/schemas/entities.py",
    dedent(
        """\
        from datetime import time
        from pydantic import BaseModel


        class NotificacionIn(BaseModel):
            usuario_id: int
            canal: str
            asunto: str | None = None
            mensaje: str
            prioridad: str = "normal"
            max_intentos: int = 3
            request_id: str | None = None


        class NotificacionPlantillaIn(BaseModel):
            usuario_id: int
            plantilla_id: int
            variables: dict[str, str]
            prioridad: str = "normal"
            max_intentos: int = 3
            request_id: str | None = None


        class PlantillaIn(BaseModel):
            nombre: str
            canal: str
            asunto_template: str | None = None
            mensaje_template: str
            variables_requeridas: list[str] | None = None
            estado: str = "activo"


        class PreferenciaIn(BaseModel):
            usuario_id: int
            canal_preferido: str
            notificaciones_activas: bool = True
            no_molestar_inicio: time | None = None
            no_molestar_fin: time | None = None
        """
    ),
)
write(
    "ms-notificaciones/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import datetime, time

        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import HistorialReintento, Notificacion, Plantilla, PreferenciaUsuario
        from app.schemas.entities import NotificacionIn, NotificacionPlantillaIn, PlantillaIn, PreferenciaIn

        router = APIRouter(tags=["ms-notificaciones"])

        PRIORITY_ORDER = {"urgente": 0, "normal": 1, "baja": 2}


        def _render_template(template: str, variables: dict[str, str]) -> str:
            text = template
            for key, value in variables.items():
                text = text.replace(f"{{{{{key}}}}}", str(value))
            return text


        def _in_do_not_disturb(pref: PreferenciaUsuario | None) -> bool:
            if not pref or not pref.no_molestar_inicio or not pref.no_molestar_fin:
                return False
            now_t = datetime.utcnow().time()
            start = pref.no_molestar_inicio
            end = pref.no_molestar_fin
            if start <= end:
                return start <= now_t <= end
            return now_t >= start or now_t <= end


        def _simulate_send(db: Session, notif: Notificacion) -> None:
            pref = db.query(PreferenciaUsuario).filter(PreferenciaUsuario.usuario_id == notif.usuario_id).first()
            if pref and not pref.notificaciones_activas:
                notif.estado = "fallida"
                db.add(HistorialReintento(notificacion_id=notif.id, numero_intento=notif.intentos + 1, resultado="fallo", detalle_error="Notificaciones desactivadas por usuario"))
                return
            if notif.prioridad in {"normal", "baja"} and _in_do_not_disturb(pref):
                # Se mantiene pendiente hasta que pase no molestar.
                return

            while notif.intentos < notif.max_intentos:
                notif.intentos += 1
                # En este proyecto el envio es simulado: se marca enviada en primer intento.
                notif.estado = "enviada"
                notif.fecha_envio = datetime.utcnow()
                db.add(HistorialReintento(notificacion_id=notif.id, numero_intento=notif.intentos, resultado="exito", detalle_error=None))
                break
            if notif.intentos >= notif.max_intentos and notif.estado != "enviada":
                notif.estado = "fallida"


        @router.post("/plantillas")
        def create_template(payload: PlantillaIn, db: Session = Depends(get_db)):
            if db.query(Plantilla).filter(Plantilla.nombre == payload.nombre).first():
                raise HTTPException(status_code=409, detail="Plantilla duplicada")
            row = Plantilla(
                nombre=payload.nombre,
                canal=payload.canal,
                asunto_template=payload.asunto_template,
                mensaje_template=payload.mensaje_template,
                variables_requeridas=",".join(payload.variables_requeridas or []),
                estado=payload.estado,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Plantilla creada")


        @router.get("/plantillas")
        def list_templates(db: Session = Depends(get_db)):
            rows = db.query(Plantilla).order_by(Plantilla.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "nombre": x.nombre,
                    "canal": x.canal,
                    "asunto_template": x.asunto_template,
                    "mensaje_template": x.mensaje_template,
                    "variables_requeridas": (x.variables_requeridas or "").split(",") if x.variables_requeridas else [],
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Plantillas listadas")


        @router.put("/plantillas/{plantilla_id}")
        def update_template(plantilla_id: int, payload: PlantillaIn, db: Session = Depends(get_db)):
            row = db.query(Plantilla).filter(Plantilla.id == plantilla_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Plantilla no encontrada")
            row.nombre = payload.nombre
            row.canal = payload.canal
            row.asunto_template = payload.asunto_template
            row.mensaje_template = payload.mensaje_template
            row.variables_requeridas = ",".join(payload.variables_requeridas or [])
            row.estado = payload.estado
            db.commit()
            return build_success_response(data={"id": plantilla_id}, message="Plantilla actualizada")


        @router.post("/plantillas/{plantilla_id}/desactivar")
        def disable_template(plantilla_id: int, db: Session = Depends(get_db)):
            row = db.query(Plantilla).filter(Plantilla.id == plantilla_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Plantilla no encontrada")
            row.estado = "inactiva"
            db.commit()
            return build_success_response(data={"id": plantilla_id}, message="Plantilla desactivada")


        @router.post("/preferencias")
        def upsert_preference(payload: PreferenciaIn, db: Session = Depends(get_db)):
            row = db.query(PreferenciaUsuario).filter(PreferenciaUsuario.usuario_id == payload.usuario_id).first()
            if row:
                row.canal_preferido = payload.canal_preferido
                row.notificaciones_activas = payload.notificaciones_activas
                row.no_molestar_inicio = payload.no_molestar_inicio
                row.no_molestar_fin = payload.no_molestar_fin
            else:
                row = PreferenciaUsuario(**payload.model_dump())
                db.add(row)
            db.commit()
            return build_success_response(data={"usuario_id": payload.usuario_id}, message="Preferencias guardadas")


        @router.get("/preferencias/{usuario_id}")
        def get_preference(usuario_id: int, db: Session = Depends(get_db)):
            row = db.query(PreferenciaUsuario).filter(PreferenciaUsuario.usuario_id == usuario_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Preferencias no encontradas")
            data = {
                "usuario_id": row.usuario_id,
                "canal_preferido": row.canal_preferido,
                "notificaciones_activas": row.notificaciones_activas,
                "no_molestar_inicio": row.no_molestar_inicio.isoformat() if row.no_molestar_inicio else None,
                "no_molestar_fin": row.no_molestar_fin.isoformat() if row.no_molestar_fin else None,
            }
            return build_success_response(data=data, message="Preferencias consultadas")


        @router.post("/enviar")
        def send_notification(payload: NotificacionIn, db: Session = Depends(get_db)):
            notif = Notificacion(**payload.model_dump(), estado="pendiente")
            db.add(notif)
            db.commit()
            db.refresh(notif)
            _simulate_send(db, notif)
            db.commit()
            return build_success_response(data={"id": notif.id, "estado": notif.estado}, message="Notificacion procesada")


        @router.post("/enviar-con-plantilla")
        def send_with_template(payload: NotificacionPlantillaIn, db: Session = Depends(get_db)):
            tpl = db.query(Plantilla).filter(Plantilla.id == payload.plantilla_id, Plantilla.estado == "activo").first()
            if not tpl:
                raise HTTPException(status_code=404, detail="Plantilla no encontrada o inactiva")
            required = [x for x in (tpl.variables_requeridas or "").split(",") if x]
            missing = [x for x in required if x not in payload.variables]
            if missing:
                raise HTTPException(status_code=400, detail=f"Faltan variables requeridas: {missing}")
            asunto = _render_template(tpl.asunto_template or "", payload.variables) if tpl.asunto_template else None
            mensaje = _render_template(tpl.mensaje_template, payload.variables)
            notif = Notificacion(
                usuario_id=payload.usuario_id,
                canal=tpl.canal,
                asunto=asunto,
                mensaje=mensaje,
                prioridad=payload.prioridad,
                max_intentos=payload.max_intentos,
                request_id=payload.request_id,
                estado="pendiente",
            )
            db.add(notif)
            db.commit()
            db.refresh(notif)
            _simulate_send(db, notif)
            db.commit()
            return build_success_response(data={"id": notif.id, "estado": notif.estado}, message="Notificacion con plantilla procesada")


        @router.post("/enviar-masivo")
        def send_massive(
            usuario_ids: list[int],
            canal: str,
            asunto: str | None,
            mensaje: str,
            prioridad: str = "normal",
            max_intentos: int = 3,
            request_id: str | None = None,
            db: Session = Depends(get_db),
        ):
            created = []
            for user_id in usuario_ids:
                notif = Notificacion(
                    usuario_id=user_id,
                    canal=canal,
                    asunto=asunto,
                    mensaje=mensaje,
                    prioridad=prioridad,
                    max_intentos=max_intentos,
                    request_id=request_id,
                    estado="pendiente",
                )
                db.add(notif)
                db.flush()
                _simulate_send(db, notif)
                created.append({"id": notif.id, "usuario_id": user_id, "estado": notif.estado})
            db.commit()
            return build_success_response(data={"notificaciones": created}, message="Envio masivo procesado")


        @router.get("/pendientes")
        def list_pending(db: Session = Depends(get_db)):
            rows = db.query(Notificacion).filter(Notificacion.estado == "pendiente").all()
            rows = sorted(rows, key=lambda x: PRIORITY_ORDER.get(x.prioridad, 99))
            data = [{"id": x.id, "usuario_id": x.usuario_id, "prioridad": x.prioridad, "estado": x.estado} for x in rows]
            return build_success_response(data=data, message="Notificaciones pendientes")


        @router.post("/notificaciones/{notificacion_id}/leida")
        def mark_read(notificacion_id: int, db: Session = Depends(get_db)):
            row = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Notificacion no encontrada")
            row.estado = "leida"
            row.fecha_lectura = datetime.utcnow()
            db.commit()
            return build_success_response(data={"id": notificacion_id}, message="Notificacion marcada como leida")


        @router.get("/usuarios/{usuario_id}/no-leidas")
        def unread_by_user(usuario_id: int, db: Session = Depends(get_db)):
            rows = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id, Notificacion.estado != "leida").order_by(Notificacion.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "canal": x.canal,
                    "asunto": x.asunto,
                    "mensaje": x.mensaje,
                    "prioridad": x.prioridad,
                    "estado": x.estado,
                    "fecha_envio": x.fecha_envio.isoformat() if x.fecha_envio else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="No leidas del usuario")
        """
    ),
)

# ms-auditoria
write("ms-auditoria/requirements.txt", COMMON_REQ)
write(
    "ms-auditoria/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-auditoria
        SERVICE_CODE=AUD
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_auditoria
        DEFAULT_RETENTION_DAYS=30
        """
    ),
)
write(
    "ms-auditoria/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_auditoria;
        \\c db_auditoria

        CREATE TABLE IF NOT EXISTS aud_eventos (
            id SERIAL PRIMARY KEY,
            fecha_hora TIMESTAMP NOT NULL DEFAULT NOW(),
            request_id VARCHAR(80),
            microservicio VARCHAR(80) NOT NULL,
            funcionalidad VARCHAR(140),
            metodo VARCHAR(20),
            codigo_respuesta INTEGER,
            duracion_ms INTEGER,
            usuario_id INTEGER,
            detalle TEXT
        );

        CREATE TABLE IF NOT EXISTS aud_retencion (
            id SERIAL PRIMARY KEY,
            dias_retencion INTEGER NOT NULL DEFAULT 30,
            estado VARCHAR(20) NOT NULL DEFAULT 'activa',
            ultima_rotacion TIMESTAMP,
            registros_eliminados_ultima_rotacion INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS aud_estadisticas (
            id SERIAL PRIMARY KEY,
            microservicio VARCHAR(80) NOT NULL,
            periodo VARCHAR(20) NOT NULL,
            fecha DATE NOT NULL,
            total_peticiones INTEGER NOT NULL,
            total_errores INTEGER NOT NULL,
            tiempo_promedio_ms NUMERIC(10,2) NOT NULL,
            funcionalidad_mas_utilizada VARCHAR(140),
            fecha_calculo TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-auditoria/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-auditoria"
            SERVICE_CODE: str = "AUD"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_auditoria"
            DEFAULT_RETENTION_DAYS: int = 30
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)
write(
    "ms-auditoria/app/models/entities.py",
    dedent(
        """\
        from datetime import date, datetime
        from sqlalchemy import DATE, DateTime, Integer, Numeric, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class EventoLog(Base):
            __tablename__ = "aud_eventos"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            request_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
            microservicio: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
            funcionalidad: Mapped[str | None] = mapped_column(String(140), nullable=True)
            metodo: Mapped[str | None] = mapped_column(String(20), nullable=True)
            codigo_respuesta: Mapped[int | None] = mapped_column(Integer, nullable=True)
            duracion_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
            usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
            detalle: Mapped[str | None] = mapped_column(Text, nullable=True)


        class ConfigRetencion(Base):
            __tablename__ = "aud_retencion"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            dias_retencion: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
            ultima_rotacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            registros_eliminados_ultima_rotacion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


        class EstadisticaServicio(Base):
            __tablename__ = "aud_estadisticas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            microservicio: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
            periodo: Mapped[str] = mapped_column(String(20), nullable=False)
            fecha: Mapped[date] = mapped_column(DATE, nullable=False)
            total_peticiones: Mapped[int] = mapped_column(Integer, nullable=False)
            total_errores: Mapped[int] = mapped_column(Integer, nullable=False)
            tiempo_promedio_ms: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
            funcionalidad_mas_utilizada: Mapped[str | None] = mapped_column(String(140), nullable=True)
            fecha_calculo: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
        """
    ),
)
write(
    "ms-auditoria/app/schemas/entities.py",
    dedent(
        """\
        from datetime import datetime
        from pydantic import BaseModel


        class EventoIn(BaseModel):
            fecha_hora: datetime | None = None
            request_id: str | None = None
            microservicio: str
            funcionalidad: str | None = None
            metodo: str | None = None
            codigo_respuesta: int | None = None
            duracion_ms: int | None = None
            usuario_id: int | None = None
            detalle: str | None = None


        class RetencionIn(BaseModel):
            dias_retencion: int
            estado: str = "activa"
        """
    ),
)
write(
    "ms-auditoria/app/db/init_db.py",
    dedent(
        """\
        from app.core.config import settings
        from app.db.session import Base, SessionLocal, engine
        from app.models.entities import ConfigRetencion, EstadisticaServicio, EventoLog  # noqa: F401


        def init_db() -> None:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                if not db.query(ConfigRetencion).first():
                    db.add(ConfigRetencion(dias_retencion=settings.DEFAULT_RETENTION_DAYS, estado="activa"))
                    db.commit()
            finally:
                db.close()
        """
    ),
)
write(
    "ms-auditoria/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import datetime, timedelta

        from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
        from sqlalchemy import func
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import ConfigRetencion, EstadisticaServicio, EventoLog
        from app.schemas.entities import EventoIn, RetencionIn

        router = APIRouter(tags=["ms-auditoria"])


        def _save_logs_sync(db: Session, events: list[EventoIn]) -> None:
            for ev in events:
                db.add(EventoLog(**ev.model_dump()))
            db.commit()


        @router.post("/logs")
        def ingest_logs(payload: list[EventoIn], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
            if not payload:
                raise HTTPException(status_code=400, detail="Payload vacio")
            # Fire-and-forget: responde y procesa en segundo plano.
            background_tasks.add_task(_save_logs_sync, db, payload)
            return build_success_response(data={"recibidos": len(payload)}, message="Logs recibidos para procesamiento")


        @router.post("/log")
        def ingest_log(payload: EventoIn, db: Session = Depends(get_db)):
            db.add(EventoLog(**payload.model_dump()))
            db.commit()
            return build_success_response(data={"ok": True}, message="Log almacenado")


        @router.get("/traza/{request_id}")
        def trace_by_request_id(request_id: str, page: int = Query(default=1, ge=1), size: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
            query = db.query(EventoLog).filter(EventoLog.request_id == request_id).order_by(EventoLog.fecha_hora.asc())
            total = query.count()
            rows = query.offset((page - 1) * size).limit(size).all()
            data = [
                {
                    "fecha_hora": x.fecha_hora.isoformat() if x.fecha_hora else None,
                    "request_id": x.request_id,
                    "microservicio": x.microservicio,
                    "funcionalidad": x.funcionalidad,
                    "metodo": x.metodo,
                    "codigo_respuesta": x.codigo_respuesta,
                    "duracion_ms": x.duracion_ms,
                    "usuario_id": x.usuario_id,
                    "detalle": x.detalle,
                }
                for x in rows
            ]
            return build_success_response(data={"items": data, "total": total, "page": page, "size": size}, message="Traza por request_id")


        @router.get("/logs")
        def search_logs(
            microservicio: str | None = None,
            fecha_inicio: str | None = None,
            fecha_fin: str | None = None,
            page: int = Query(default=1, ge=1),
            size: int = Query(default=50, ge=1, le=200),
            db: Session = Depends(get_db),
        ):
            query = db.query(EventoLog)
            if microservicio:
                query = query.filter(EventoLog.microservicio == microservicio)
            if fecha_inicio:
                query = query.filter(EventoLog.fecha_hora >= fecha_inicio)
            if fecha_fin:
                query = query.filter(EventoLog.fecha_hora <= fecha_fin)
            total = query.count()
            rows = query.order_by(EventoLog.fecha_hora.desc()).offset((page - 1) * size).limit(size).all()
            data = [
                {
                    "id": x.id,
                    "fecha_hora": x.fecha_hora.isoformat() if x.fecha_hora else None,
                    "request_id": x.request_id,
                    "microservicio": x.microservicio,
                    "funcionalidad": x.funcionalidad,
                    "metodo": x.metodo,
                    "codigo_respuesta": x.codigo_respuesta,
                    "duracion_ms": x.duracion_ms,
                    "usuario_id": x.usuario_id,
                    "detalle": x.detalle,
                }
                for x in rows
            ]
            return build_success_response(data={"items": data, "total": total, "page": page, "size": size}, message="Busqueda de logs")


        @router.get("/retencion")
        def get_retention(db: Session = Depends(get_db)):
            row = db.query(ConfigRetencion).first()
            if not row:
                raise HTTPException(status_code=404, detail="Configuracion de retencion no encontrada")
            return build_success_response(
                data={
                    "dias_retencion": row.dias_retencion,
                    "estado": row.estado,
                    "ultima_rotacion": row.ultima_rotacion.isoformat() if row.ultima_rotacion else None,
                    "registros_eliminados_ultima_rotacion": row.registros_eliminados_ultima_rotacion,
                },
                message="Configuracion de retencion",
            )


        @router.put("/retencion")
        def update_retention(payload: RetencionIn, db: Session = Depends(get_db)):
            row = db.query(ConfigRetencion).first()
            if not row:
                row = ConfigRetencion()
                db.add(row)
            row.dias_retencion = payload.dias_retencion
            row.estado = payload.estado
            db.commit()
            return build_success_response(data={"dias_retencion": row.dias_retencion, "estado": row.estado}, message="Retencion actualizada")


        @router.post("/rotacion/ejecutar")
        def rotate_logs(db: Session = Depends(get_db)):
            cfg = db.query(ConfigRetencion).first()
            if not cfg:
                raise HTTPException(status_code=404, detail="Configuracion de retencion no encontrada")
            cutoff = datetime.utcnow() - timedelta(days=cfg.dias_retencion)
            to_delete = db.query(EventoLog).filter(EventoLog.fecha_hora < cutoff)
            count = to_delete.count()
            to_delete.delete(synchronize_session=False)
            cfg.ultima_rotacion = datetime.utcnow()
            cfg.registros_eliminados_ultima_rotacion = count
            db.commit()
            return build_success_response(data={"registros_eliminados": count}, message="Rotacion ejecutada")


        @router.post("/estadisticas/recalcular")
        def recalc_stats(periodo: str = "diario", db: Session = Depends(get_db)):
            # Simplificado: calcula sobre todos los registros actuales por microservicio.
            rows = db.query(EventoLog.microservicio).distinct().all()
            now_date = datetime.utcnow().date()
            created = 0
            for row in rows:
                micro = row[0]
                logs = db.query(EventoLog).filter(EventoLog.microservicio == micro).all()
                if not logs:
                    continue
                total = len(logs)
                errors = sum(1 for l in logs if (l.codigo_respuesta or 200) >= 400)
                avg = sum((l.duracion_ms or 0) for l in logs) / total
                freq = {}
                for l in logs:
                    key = l.funcionalidad or "N/A"
                    freq[key] = freq.get(key, 0) + 1
                top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[0][0]
                db.add(
                    EstadisticaServicio(
                        microservicio=micro,
                        periodo=periodo,
                        fecha=now_date,
                        total_peticiones=total,
                        total_errores=errors,
                        tiempo_promedio_ms=avg,
                        funcionalidad_mas_utilizada=top,
                    )
                )
                created += 1
            db.commit()
            return build_success_response(data={"estadisticas_generadas": created}, message="Estadisticas recalculadas")


        @router.get("/estadisticas")
        def get_stats(microservicio: str | None = None, page: int = Query(default=1, ge=1), size: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
            query = db.query(EstadisticaServicio)
            if microservicio:
                query = query.filter(EstadisticaServicio.microservicio == microservicio)
            total = query.count()
            rows = query.order_by(EstadisticaServicio.id.desc()).offset((page - 1) * size).limit(size).all()
            data = [
                {
                    "id": x.id,
                    "microservicio": x.microservicio,
                    "periodo": x.periodo,
                    "fecha": x.fecha.isoformat() if x.fecha else None,
                    "total_peticiones": x.total_peticiones,
                    "total_errores": x.total_errores,
                    "tiempo_promedio_ms": float(x.tiempo_promedio_ms),
                    "funcionalidad_mas_utilizada": x.funcionalidad_mas_utilizada,
                    "fecha_calculo": x.fecha_calculo.isoformat() if x.fecha_calculo else None,
                }
                for x in rows
            ]
            return build_success_response(data={"items": data, "total": total, "page": page, "size": size}, message="Estadisticas consultadas")
        """
    ),
)

print("Transversales implementados: notificaciones y auditoria.")
