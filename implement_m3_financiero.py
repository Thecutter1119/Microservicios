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
    httpx==0.27.2
    """
)

# ---------------- ms-presupuesto ----------------
write("ms-presupuesto/requirements.txt", COMMON_REQ)
write(
    "ms-presupuesto/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-presupuesto
        SERVICE_CODE=PRE
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_presupuesto
        ALERTA_DEFAULT_PERCENT=80
        """
    ),
)
write(
    "ms-presupuesto/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_presupuesto;
        \\c db_presupuesto

        CREATE TABLE IF NOT EXISTS pre_presupuestos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(140) NOT NULL,
            periodo VARCHAR(40) NOT NULL,
            monto_total NUMERIC(14,2) NOT NULL,
            monto_ejecutado NUMERIC(14,2) NOT NULL DEFAULT 0,
            monto_disponible NUMERIC(14,2) NOT NULL DEFAULT 0,
            estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
            approved_by INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS pre_partidas (
            id SERIAL PRIMARY KEY,
            presupuesto_id INTEGER NOT NULL REFERENCES pre_presupuestos(id),
            nombre VARCHAR(140) NOT NULL,
            area_destino VARCHAR(120) NOT NULL,
            monto_asignado NUMERIC(14,2) NOT NULL,
            monto_ejecutado NUMERIC(14,2) NOT NULL DEFAULT 0,
            monto_disponible NUMERIC(14,2) NOT NULL DEFAULT 0,
            porcentaje_alerta INTEGER NOT NULL DEFAULT 80,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS pre_reasignaciones (
            id SERIAL PRIMARY KEY,
            partida_origen_id INTEGER NOT NULL REFERENCES pre_partidas(id),
            partida_destino_id INTEGER NOT NULL REFERENCES pre_partidas(id),
            monto NUMERIC(14,2) NOT NULL,
            motivo TEXT NOT NULL,
            solicitado_por INTEGER,
            aprobado_por INTEGER,
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-presupuesto/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-presupuesto"
            SERVICE_CODE: str = "PRE"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_presupuesto"
            ALERTA_DEFAULT_PERCENT: int = 80
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)
write(
    "ms-presupuesto/app/models/entities.py",
    dedent(
        """\
        from datetime import datetime
        from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class Presupuesto(Base):
            __tablename__ = "pre_presupuestos"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(140), nullable=False)
            periodo: Mapped[str] = mapped_column(String(40), nullable=False)
            monto_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            monto_ejecutado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            monto_disponible: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="borrador", nullable=False)
            approved_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
            approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Partida(Base):
            __tablename__ = "pre_partidas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            presupuesto_id: Mapped[int] = mapped_column(ForeignKey("pre_presupuestos.id"), nullable=False, index=True)
            nombre: Mapped[str] = mapped_column(String(140), nullable=False)
            area_destino: Mapped[str] = mapped_column(String(120), nullable=False)
            monto_asignado: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            monto_ejecutado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            monto_disponible: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            porcentaje_alerta: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Reasignacion(Base):
            __tablename__ = "pre_reasignaciones"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            partida_origen_id: Mapped[int] = mapped_column(ForeignKey("pre_partidas.id"), nullable=False)
            partida_destino_id: Mapped[int] = mapped_column(ForeignKey("pre_partidas.id"), nullable=False)
            monto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            motivo: Mapped[str] = mapped_column(Text, nullable=False)
            solicitado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            aprobado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
        """
    ),
)
write(
    "ms-presupuesto/app/schemas/entities.py",
    dedent(
        """\
        from datetime import datetime
        from pydantic import BaseModel, ConfigDict


        class PresupuestoIn(BaseModel):
            nombre: str
            periodo: str
            monto_total: float


        class PresupuestoUpdate(BaseModel):
            nombre: str | None = None
            periodo: str | None = None
            monto_total: float | None = None
            estado: str | None = None


        class PartidaIn(BaseModel):
            presupuesto_id: int
            nombre: str
            area_destino: str
            monto_asignado: float
            porcentaje_alerta: int = 80
            estado: str = "activo"


        class PartidaUpdate(BaseModel):
            nombre: str | None = None
            area_destino: str | None = None
            monto_asignado: float | None = None
            porcentaje_alerta: int | None = None
            estado: str | None = None


        class ReasignacionIn(BaseModel):
            partida_origen_id: int
            partida_destino_id: int
            monto: float
            motivo: str
            solicitado_por: int | None = None
        """
    ),
)
write(
    "ms-presupuesto/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import datetime

        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import Partida, Presupuesto, Reasignacion
        from app.schemas.entities import PartidaIn, PartidaUpdate, PresupuestoIn, PresupuestoUpdate, ReasignacionIn

        router = APIRouter(tags=["ms-presupuesto"])


        def _sync_presupuesto_totals(db: Session, presupuesto_id: int) -> None:
            presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
            if not presupuesto:
                return
            partidas = db.query(Partida).filter(Partida.presupuesto_id == presupuesto_id).all()
            ejecutado = sum(float(x.monto_ejecutado) for x in partidas)
            presupuesto.monto_ejecutado = ejecutado
            presupuesto.monto_disponible = float(presupuesto.monto_total) - ejecutado


        @router.post("/presupuestos")
        def create_budget(payload: PresupuestoIn, db: Session = Depends(get_db)):
            row = Presupuesto(
                **payload.model_dump(),
                monto_ejecutado=0,
                monto_disponible=payload.monto_total,
                estado="borrador",
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Presupuesto creado")


        @router.get("/presupuestos")
        def list_budgets(db: Session = Depends(get_db)):
            rows = db.query(Presupuesto).order_by(Presupuesto.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "nombre": x.nombre,
                    "periodo": x.periodo,
                    "monto_total": float(x.monto_total),
                    "monto_ejecutado": float(x.monto_ejecutado),
                    "monto_disponible": float(x.monto_disponible),
                    "estado": x.estado,
                    "approved_by": x.approved_by,
                    "approved_at": x.approved_at.isoformat() if x.approved_at else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Presupuestos listados")


        @router.put("/presupuestos/{presupuesto_id}")
        def update_budget(presupuesto_id: int, payload: PresupuestoUpdate, db: Session = Depends(get_db)):
            row = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            _sync_presupuesto_totals(db, presupuesto_id)
            db.commit()
            return build_success_response(data={"id": presupuesto_id}, message="Presupuesto actualizado")


        @router.post("/presupuestos/{presupuesto_id}/aprobar")
        def approve_budget(presupuesto_id: int, approved_by: int, db: Session = Depends(get_db)):
            row = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
            row.estado = "aprobado"
            row.approved_by = approved_by
            row.approved_at = datetime.utcnow()
            db.commit()
            return build_success_response(data={"id": presupuesto_id}, message="Presupuesto aprobado")


        @router.post("/partidas")
        def create_item(payload: PartidaIn, db: Session = Depends(get_db)):
            if not db.query(Presupuesto).filter(Presupuesto.id == payload.presupuesto_id).first():
                raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
            row = Partida(
                **payload.model_dump(),
                monto_ejecutado=0,
                monto_disponible=payload.monto_asignado,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            _sync_presupuesto_totals(db, row.presupuesto_id)
            db.commit()
            return build_success_response(data={"id": row.id}, message="Partida creada")


        @router.get("/partidas")
        def list_items(db: Session = Depends(get_db)):
            rows = db.query(Partida).order_by(Partida.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "presupuesto_id": x.presupuesto_id,
                    "nombre": x.nombre,
                    "area_destino": x.area_destino,
                    "monto_asignado": float(x.monto_asignado),
                    "monto_ejecutado": float(x.monto_ejecutado),
                    "monto_disponible": float(x.monto_disponible),
                    "porcentaje_alerta": x.porcentaje_alerta,
                    "estado": x.estado,
                    "alerta": (float(x.monto_ejecutado) / float(x.monto_asignado) * 100) >= x.porcentaje_alerta if float(x.monto_asignado) > 0 else False,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Partidas listadas")


        @router.put("/partidas/{partida_id}")
        def update_item(partida_id: int, payload: PartidaUpdate, db: Session = Depends(get_db)):
            row = db.query(Partida).filter(Partida.id == partida_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Partida no encontrada")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            row.monto_disponible = float(row.monto_asignado) - float(row.monto_ejecutado)
            _sync_presupuesto_totals(db, row.presupuesto_id)
            db.commit()
            return build_success_response(data={"id": partida_id}, message="Partida actualizada")


        @router.get("/partidas/{partida_id}/saldo")
        def saldo_item(partida_id: int, db: Session = Depends(get_db)):
            row = db.query(Partida).filter(Partida.id == partida_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Partida no encontrada")
            return build_success_response(data={"partida_id": partida_id, "saldo_disponible": float(row.monto_disponible)}, message="Saldo consultado")


        @router.post("/partidas/{partida_id}/consumir")
        def consume_item(partida_id: int, monto: float, db: Session = Depends(get_db)):
            row = db.query(Partida).filter(Partida.id == partida_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Partida no encontrada")
            if monto <= 0:
                raise HTTPException(status_code=400, detail="Monto invalido")
            if float(row.monto_disponible) < monto:
                raise HTTPException(status_code=409, detail="Saldo insuficiente")
            row.monto_ejecutado = float(row.monto_ejecutado) + monto
            row.monto_disponible = float(row.monto_asignado) - float(row.monto_ejecutado)
            _sync_presupuesto_totals(db, row.presupuesto_id)
            db.commit()
            alerta = (float(row.monto_ejecutado) / float(row.monto_asignado) * 100) >= row.porcentaje_alerta if float(row.monto_asignado) > 0 else False
            return build_success_response(
                data={"partida_id": partida_id, "monto_disponible": float(row.monto_disponible), "alerta_umbral": alerta},
                message="Consumo registrado",
            )


        @router.post("/reasignaciones")
        def create_reallocation(payload: ReasignacionIn, db: Session = Depends(get_db)):
            if payload.partida_origen_id == payload.partida_destino_id:
                raise HTTPException(status_code=400, detail="Partida origen y destino no pueden ser iguales")
            origen = db.query(Partida).filter(Partida.id == payload.partida_origen_id).first()
            destino = db.query(Partida).filter(Partida.id == payload.partida_destino_id).first()
            if not origen or not destino:
                raise HTTPException(status_code=404, detail="Partida origen o destino no encontrada")
            row = Reasignacion(**payload.model_dump(), estado="pendiente")
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Reasignacion solicitada")


        @router.post("/reasignaciones/{reasignacion_id}/aprobar")
        def approve_reallocation(reasignacion_id: int, aprobado_por: int, db: Session = Depends(get_db)):
            row = db.query(Reasignacion).filter(Reasignacion.id == reasignacion_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Reasignacion no encontrada")
            if row.estado != "pendiente":
                raise HTTPException(status_code=409, detail="La reasignacion no esta pendiente")
            origen = db.query(Partida).filter(Partida.id == row.partida_origen_id).first()
            destino = db.query(Partida).filter(Partida.id == row.partida_destino_id).first()
            if float(origen.monto_disponible) < float(row.monto):
                raise HTTPException(status_code=409, detail="Saldo insuficiente en partida origen")
            origen.monto_asignado = float(origen.monto_asignado) - float(row.monto)
            origen.monto_disponible = float(origen.monto_asignado) - float(origen.monto_ejecutado)
            destino.monto_asignado = float(destino.monto_asignado) + float(row.monto)
            destino.monto_disponible = float(destino.monto_asignado) - float(destino.monto_ejecutado)
            row.estado = "aprobada"
            row.aprobado_por = aprobado_por
            _sync_presupuesto_totals(db, origen.presupuesto_id)
            if destino.presupuesto_id != origen.presupuesto_id:
                _sync_presupuesto_totals(db, destino.presupuesto_id)
            db.commit()
            return build_success_response(data={"id": reasignacion_id}, message="Reasignacion aprobada")


        @router.post("/reasignaciones/{reasignacion_id}/rechazar")
        def reject_reallocation(reasignacion_id: int, aprobado_por: int, db: Session = Depends(get_db)):
            row = db.query(Reasignacion).filter(Reasignacion.id == reasignacion_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Reasignacion no encontrada")
            row.estado = "rechazada"
            row.aprobado_por = aprobado_por
            db.commit()
            return build_success_response(data={"id": reasignacion_id}, message="Reasignacion rechazada")


        @router.get("/presupuestos/{presupuesto_id}/resumen")
        def summary_budget(presupuesto_id: int, db: Session = Depends(get_db)):
            presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
            if not presupuesto:
                raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
            partidas = db.query(Partida).filter(Partida.presupuesto_id == presupuesto_id).all()
            data = {
                "presupuesto": {
                    "id": presupuesto.id,
                    "nombre": presupuesto.nombre,
                    "periodo": presupuesto.periodo,
                    "estado": presupuesto.estado,
                    "monto_total": float(presupuesto.monto_total),
                    "monto_ejecutado": float(presupuesto.monto_ejecutado),
                    "monto_disponible": float(presupuesto.monto_disponible),
                },
                "partidas": [
                    {
                        "id": p.id,
                        "nombre": p.nombre,
                        "area_destino": p.area_destino,
                        "monto_asignado": float(p.monto_asignado),
                        "monto_ejecutado": float(p.monto_ejecutado),
                        "monto_disponible": float(p.monto_disponible),
                    }
                    for p in partidas
                ],
            }
            return build_success_response(data=data, message="Resumen de ejecucion")
        """
    ),
)

# ---------------- ms-gastos ----------------
write("ms-gastos/requirements.txt", COMMON_REQ)
write(
    "ms-gastos/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-gastos
        SERVICE_CODE=GAS
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_gastos
        PRE_BASE_URL=http://localhost:8007
        NOVEDAD_ESCALACION_UMBRAL=1000000
        """
    ),
)
write(
    "ms-gastos/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_gastos;
        \\c db_gastos

        CREATE TABLE IF NOT EXISTS gas_categorias (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL UNIQUE,
            descripcion TEXT,
            requiere_aprobacion_especial BOOLEAN NOT NULL DEFAULT FALSE,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo'
        );

        CREATE TABLE IF NOT EXISTS gas_gastos (
            id SERIAL PRIMARY KEY,
            descripcion TEXT NOT NULL,
            monto NUMERIC(14,2) NOT NULL,
            categoria_id INTEGER NOT NULL REFERENCES gas_categorias(id),
            partida_presupuestal_id INTEGER NOT NULL,
            proveedor_id INTEGER,
            estado VARCHAR(20) NOT NULL DEFAULT 'solicitado',
            solicitado_por INTEGER,
            fecha_solicitud TIMESTAMP NOT NULL DEFAULT NOW(),
            aprobado_por INTEGER,
            fecha_aprobacion TIMESTAMP,
            fecha_pago TIMESTAMP,
            observaciones TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS gas_novedades (
            id SERIAL PRIMARY KEY,
            gasto_id INTEGER NOT NULL REFERENCES gas_gastos(id),
            tipo_novedad VARCHAR(40) NOT NULL,
            descripcion TEXT NOT NULL,
            monto_impacto NUMERIC(14,2) NOT NULL,
            reportado_por INTEGER,
            fecha_reporte TIMESTAMP NOT NULL DEFAULT NOW(),
            estado VARCHAR(20) NOT NULL DEFAULT 'abierta'
        );

        CREATE TABLE IF NOT EXISTS gas_aprobaciones (
            id SERIAL PRIMARY KEY,
            gasto_id INTEGER NOT NULL REFERENCES gas_gastos(id),
            aprobador_id INTEGER,
            decision VARCHAR(20) NOT NULL,
            comentario TEXT,
            fecha TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-gastos/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-gastos"
            SERVICE_CODE: str = "GAS"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_gastos"
            PRE_BASE_URL: str = "http://localhost:8007"
            NOVEDAD_ESCALACION_UMBRAL: float = 1000000
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)
write(
    "ms-gastos/app/models/entities.py",
    dedent(
        """\
        from datetime import datetime
        from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class CategoriaGasto(Base):
            __tablename__ = "gas_categorias"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            requiere_aprobacion_especial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)


        class Gasto(Base):
            __tablename__ = "gas_gastos"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            descripcion: Mapped[str] = mapped_column(Text, nullable=False)
            monto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            categoria_id: Mapped[int] = mapped_column(ForeignKey("gas_categorias.id"), nullable=False)
            partida_presupuestal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            proveedor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
            estado: Mapped[str] = mapped_column(String(20), default="solicitado", nullable=False)
            solicitado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            fecha_solicitud: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            aprobado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            fecha_aprobacion: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            fecha_pago: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Novedad(Base):
            __tablename__ = "gas_novedades"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            gasto_id: Mapped[int] = mapped_column(ForeignKey("gas_gastos.id"), nullable=False, index=True)
            tipo_novedad: Mapped[str] = mapped_column(String(40), nullable=False)
            descripcion: Mapped[str] = mapped_column(Text, nullable=False)
            monto_impacto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            reportado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            fecha_reporte: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            estado: Mapped[str] = mapped_column(String(20), default="abierta", nullable=False)


        class Aprobacion(Base):
            __tablename__ = "gas_aprobaciones"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            gasto_id: Mapped[int] = mapped_column(ForeignKey("gas_gastos.id"), nullable=False, index=True)
            aprobador_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
            decision: Mapped[str] = mapped_column(String(20), nullable=False)
            comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
            fecha: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
        """
    ),
)
write(
    "ms-gastos/app/schemas/entities.py",
    dedent(
        """\
        from pydantic import BaseModel


        class CategoriaIn(BaseModel):
            nombre: str
            descripcion: str | None = None
            requiere_aprobacion_especial: bool = False
            estado: str = "activo"


        class GastoIn(BaseModel):
            descripcion: str
            monto: float
            categoria_id: int
            partida_presupuestal_id: int
            proveedor_id: int | None = None
            solicitado_por: int | None = None
            observaciones: str | None = None


        class GastoUpdate(BaseModel):
            descripcion: str | None = None
            monto: float | None = None
            categoria_id: int | None = None
            partida_presupuestal_id: int | None = None
            proveedor_id: int | None = None
            observaciones: str | None = None


        class NovedadIn(BaseModel):
            gasto_id: int
            tipo_novedad: str
            descripcion: str
            monto_impacto: float
            reportado_por: int | None = None


        class NovedadUpdate(BaseModel):
            descripcion: str | None = None
            monto_impacto: float | None = None
            estado: str | None = None
        """
    ),
)
write(
    "ms-gastos/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import datetime

        import httpx
        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.orm import Session

        from app.core.config import settings
        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import Aprobacion, CategoriaGasto, Gasto, Novedad
        from app.schemas.entities import CategoriaIn, GastoIn, GastoUpdate, NovedadIn, NovedadUpdate

        router = APIRouter(tags=["ms-gastos"])

        ALLOWED_FLOW = {
            "solicitado": {"en revision"},
            "en revision": {"aprobado", "rechazado"},
            "aprobado": {"pagado"},
            "rechazado": set(),
            "pagado": set(),
        }


        async def _validate_saldo(partida_id: int, monto: float) -> bool:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(f"{settings.PRE_BASE_URL}/api/v1/partidas/{partida_id}/saldo")
                if resp.status_code >= 400:
                    raise HTTPException(status_code=404, detail="Partida presupuestal no encontrada en presupuesto")
                saldo = float(resp.json()["data"]["saldo_disponible"])
                return saldo >= monto


        async def _consume_saldo(partida_id: int, monto: float) -> dict:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(f"{settings.PRE_BASE_URL}/api/v1/partidas/{partida_id}/consumir", params={"monto": monto})
                if resp.status_code >= 400:
                    raise HTTPException(status_code=409, detail="No se pudo consumir presupuesto")
                return resp.json().get("data", {})


        @router.post("/categorias")
        def create_category(payload: CategoriaIn, db: Session = Depends(get_db)):
            if db.query(CategoriaGasto).filter(CategoriaGasto.nombre == payload.nombre).first():
                raise HTTPException(status_code=409, detail="Categoria ya existe")
            row = CategoriaGasto(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Categoria creada")


        @router.get("/categorias")
        def list_categories(db: Session = Depends(get_db)):
            rows = db.query(CategoriaGasto).order_by(CategoriaGasto.nombre.asc()).all()
            data = [
                {
                    "id": x.id,
                    "nombre": x.nombre,
                    "descripcion": x.descripcion,
                    "requiere_aprobacion_especial": x.requiere_aprobacion_especial,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Categorias listadas")


        @router.post("/gastos")
        def create_expense(payload: GastoIn, db: Session = Depends(get_db)):
            if not db.query(CategoriaGasto).filter(CategoriaGasto.id == payload.categoria_id).first():
                raise HTTPException(status_code=404, detail="Categoria no encontrada")
            row = Gasto(**payload.model_dump(), estado="solicitado")
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Gasto creado")


        @router.get("/gastos")
        def list_expenses(db: Session = Depends(get_db)):
            rows = db.query(Gasto).order_by(Gasto.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "descripcion": x.descripcion,
                    "monto": float(x.monto),
                    "categoria_id": x.categoria_id,
                    "partida_presupuestal_id": x.partida_presupuestal_id,
                    "proveedor_id": x.proveedor_id,
                    "estado": x.estado,
                    "solicitado_por": x.solicitado_por,
                    "fecha_solicitud": x.fecha_solicitud.isoformat() if x.fecha_solicitud else None,
                    "aprobado_por": x.aprobado_por,
                    "fecha_aprobacion": x.fecha_aprobacion.isoformat() if x.fecha_aprobacion else None,
                    "fecha_pago": x.fecha_pago.isoformat() if x.fecha_pago else None,
                    "observaciones": x.observaciones,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Gastos listados")


        @router.put("/gastos/{gasto_id}")
        def update_expense(gasto_id: int, payload: GastoUpdate, db: Session = Depends(get_db)):
            row = db.query(Gasto).filter(Gasto.id == gasto_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Gasto no encontrado")
            if row.estado != "solicitado":
                raise HTTPException(status_code=409, detail="Solo se puede modificar gasto en estado solicitado")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": gasto_id}, message="Gasto actualizado")


        @router.post("/gastos/{gasto_id}/estado")
        async def change_expense_state(gasto_id: int, nuevo_estado: str, aprobador_id: int | None = None, comentario: str | None = None, db: Session = Depends(get_db)):
            row = db.query(Gasto).filter(Gasto.id == gasto_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Gasto no encontrado")
            if nuevo_estado not in ALLOWED_FLOW.get(row.estado, set()):
                raise HTTPException(status_code=409, detail=f"Transicion invalida: {row.estado} -> {nuevo_estado}")

            if nuevo_estado == "aprobado":
                ok = await _validate_saldo(row.partida_presupuestal_id, float(row.monto))
                if not ok:
                    raise HTTPException(status_code=409, detail="Saldo insuficiente en partida presupuestal")
                consume_data = await _consume_saldo(row.partida_presupuestal_id, float(row.monto))
                row.aprobado_por = aprobador_id
                row.fecha_aprobacion = datetime.utcnow()
                if consume_data.get("alerta_umbral"):
                    row.observaciones = (row.observaciones or "") + " | Alerta: umbral de partida alcanzado"
            if nuevo_estado == "pagado":
                row.fecha_pago = datetime.utcnow()
            row.estado = nuevo_estado
            db.add(Aprobacion(gasto_id=row.id, aprobador_id=aprobador_id, decision=nuevo_estado, comentario=comentario))
            db.commit()
            return build_success_response(data={"id": row.id, "estado": row.estado}, message="Estado de gasto actualizado")


        @router.post("/novedades")
        def create_novedad(payload: NovedadIn, db: Session = Depends(get_db)):
            if not db.query(Gasto).filter(Gasto.id == payload.gasto_id).first():
                raise HTTPException(status_code=404, detail="Gasto no encontrado")
            estado = "escalada" if payload.monto_impacto >= settings.NOVEDAD_ESCALACION_UMBRAL else "abierta"
            row = Novedad(**payload.model_dump(), estado=estado)
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id, "estado": row.estado}, message="Novedad registrada")


        @router.get("/novedades")
        def list_novedades(db: Session = Depends(get_db)):
            rows = db.query(Novedad).order_by(Novedad.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "gasto_id": x.gasto_id,
                    "tipo_novedad": x.tipo_novedad,
                    "descripcion": x.descripcion,
                    "monto_impacto": float(x.monto_impacto),
                    "reportado_por": x.reportado_por,
                    "fecha_reporte": x.fecha_reporte.isoformat() if x.fecha_reporte else None,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Novedades listadas")


        @router.put("/novedades/{novedad_id}")
        def update_novedad(novedad_id: int, payload: NovedadUpdate, db: Session = Depends(get_db)):
            row = db.query(Novedad).filter(Novedad.id == novedad_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Novedad no encontrada")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            if float(row.monto_impacto) >= settings.NOVEDAD_ESCALACION_UMBRAL and row.estado == "abierta":
                row.estado = "escalada"
            db.commit()
            return build_success_response(data={"id": novedad_id, "estado": row.estado}, message="Novedad actualizada")


        @router.get("/aprobaciones")
        def list_approvals(gasto_id: int | None = None, db: Session = Depends(get_db)):
            query = db.query(Aprobacion)
            if gasto_id:
                query = query.filter(Aprobacion.gasto_id == gasto_id)
            rows = query.order_by(Aprobacion.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "gasto_id": x.gasto_id,
                    "aprobador_id": x.aprobador_id,
                    "decision": x.decision,
                    "comentario": x.comentario,
                    "fecha": x.fecha.isoformat() if x.fecha else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Aprobaciones listadas")
        """
    ),
)

# ---------------- ms-facturacion ----------------
write("ms-facturacion/requirements.txt", COMMON_REQ)
write(
    "ms-facturacion/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-facturacion
        SERVICE_CODE=FAC
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_facturacion
        """
    ),
)
write(
    "ms-facturacion/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_facturacion;
        \\c db_facturacion

        CREATE TABLE IF NOT EXISTS fac_conceptos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(140) NOT NULL UNIQUE,
            descripcion TEXT,
            valor_base NUMERIC(14,2) NOT NULL,
            es_recurrente BOOLEAN NOT NULL DEFAULT FALSE,
            periodicidad VARCHAR(40),
            estado VARCHAR(20) NOT NULL DEFAULT 'activo'
        );

        CREATE TABLE IF NOT EXISTS fac_facturas (
            id SERIAL PRIMARY KEY,
            numero_factura VARCHAR(40) NOT NULL UNIQUE,
            usuario_id INTEGER NOT NULL,
            fecha_emision TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_vencimiento TIMESTAMP NOT NULL,
            subtotal NUMERIC(14,2) NOT NULL DEFAULT 0,
            porcentaje_impuesto NUMERIC(6,2) NOT NULL DEFAULT 0,
            valor_impuesto NUMERIC(14,2) NOT NULL DEFAULT 0,
            total NUMERIC(14,2) NOT NULL DEFAULT 0,
            estado VARCHAR(20) NOT NULL DEFAULT 'emitida',
            fecha_pago TIMESTAMP,
            observaciones TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS fac_detalles_factura (
            id SERIAL PRIMARY KEY,
            factura_id INTEGER NOT NULL REFERENCES fac_facturas(id),
            concepto_id INTEGER NOT NULL REFERENCES fac_conceptos(id),
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            valor_unitario NUMERIC(14,2) NOT NULL,
            subtotal_linea NUMERIC(14,2) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS fac_estados_cuenta (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL UNIQUE,
            total_facturado NUMERIC(14,2) NOT NULL DEFAULT 0,
            total_pagado NUMERIC(14,2) NOT NULL DEFAULT 0,
            saldo_pendiente NUMERIC(14,2) NOT NULL DEFAULT 0,
            facturas_vencidas INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-facturacion/app/models/entities.py",
    dedent(
        """\
        from datetime import datetime
        from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class ConceptoCobro(Base):
            __tablename__ = "fac_conceptos"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            valor_base: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            es_recurrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
            periodicidad: Mapped[str | None] = mapped_column(String(40), nullable=True)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)


        class Factura(Base):
            __tablename__ = "fac_facturas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            numero_factura: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
            usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
            subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            porcentaje_impuesto: Mapped[float] = mapped_column(Numeric(6, 2), default=0, nullable=False)
            valor_impuesto: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            total: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="emitida", nullable=False)
            fecha_pago: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class FacturaDetalle(Base):
            __tablename__ = "fac_detalles_factura"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            factura_id: Mapped[int] = mapped_column(ForeignKey("fac_facturas.id"), nullable=False, index=True)
            concepto_id: Mapped[int] = mapped_column(ForeignKey("fac_conceptos.id"), nullable=False, index=True)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
            valor_unitario: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            subtotal_linea: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)


        class EstadoCuenta(Base):
            __tablename__ = "fac_estados_cuenta"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            usuario_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
            total_facturado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            total_pagado: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            saldo_pendiente: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            facturas_vencidas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
        """
    ),
)
write(
    "ms-facturacion/app/schemas/entities.py",
    dedent(
        """\
        from datetime import datetime
        from pydantic import BaseModel


        class ConceptoIn(BaseModel):
            nombre: str
            descripcion: str | None = None
            valor_base: float
            es_recurrente: bool = False
            periodicidad: str | None = None
            estado: str = "activo"


        class FacturaDetalleIn(BaseModel):
            concepto_id: int
            descripcion: str | None = None
            cantidad: int
            valor_unitario: float


        class FacturaIn(BaseModel):
            usuario_id: int
            fecha_vencimiento: datetime
            porcentaje_impuesto: float = 0
            observaciones: str | None = None
            detalles: list[FacturaDetalleIn]
        """
    ),
)
write(
    "ms-facturacion/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import datetime

        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy import func
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import ConceptoCobro, EstadoCuenta, Factura, FacturaDetalle
        from app.schemas.entities import ConceptoIn, FacturaIn

        router = APIRouter(tags=["ms-facturacion"])


        def _sync_estado_cuenta(db: Session, usuario_id: int) -> None:
            facturas = db.query(Factura).filter(Factura.usuario_id == usuario_id).all()
            total_facturado = sum(float(x.total) for x in facturas)
            total_pagado = sum(float(x.total) for x in facturas if x.estado == "pagada")
            pendientes = sum(float(x.total) for x in facturas if x.estado in {"emitida", "vencida"})
            vencidas = sum(1 for x in facturas if x.estado == "vencida")
            row = db.query(EstadoCuenta).filter(EstadoCuenta.usuario_id == usuario_id).first()
            if not row:
                row = EstadoCuenta(usuario_id=usuario_id)
                db.add(row)
            row.total_facturado = total_facturado
            row.total_pagado = total_pagado
            row.saldo_pendiente = pendientes
            row.facturas_vencidas = vencidas


        def _next_invoice_number(db: Session) -> str:
            count = db.query(func.count(Factura.id)).scalar() or 0
            return f"FAC-{count + 1:08d}"


        @router.post("/conceptos")
        def create_concept(payload: ConceptoIn, db: Session = Depends(get_db)):
            if db.query(ConceptoCobro).filter(ConceptoCobro.nombre == payload.nombre).first():
                raise HTTPException(status_code=409, detail="Concepto ya existe")
            row = ConceptoCobro(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Concepto creado")


        @router.get("/conceptos")
        def list_concepts(db: Session = Depends(get_db)):
            rows = db.query(ConceptoCobro).order_by(ConceptoCobro.nombre.asc()).all()
            data = [
                {
                    "id": x.id,
                    "nombre": x.nombre,
                    "descripcion": x.descripcion,
                    "valor_base": float(x.valor_base),
                    "es_recurrente": x.es_recurrente,
                    "periodicidad": x.periodicidad,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Conceptos listados")


        @router.put("/conceptos/{concepto_id}")
        def update_concept(concepto_id: int, payload: ConceptoIn, db: Session = Depends(get_db)):
            row = db.query(ConceptoCobro).filter(ConceptoCobro.id == concepto_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Concepto no encontrado")
            for key, value in payload.model_dump().items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": concepto_id}, message="Concepto actualizado")


        @router.post("/facturas")
        def create_invoice(payload: FacturaIn, db: Session = Depends(get_db)):
            if not payload.detalles:
                raise HTTPException(status_code=400, detail="La factura debe tener al menos un detalle")
            numero = _next_invoice_number(db)
            subtotal = 0.0
            invoice = Factura(
                numero_factura=numero,
                usuario_id=payload.usuario_id,
                fecha_vencimiento=payload.fecha_vencimiento,
                porcentaje_impuesto=payload.porcentaje_impuesto,
                estado="emitida",
                observaciones=payload.observaciones,
            )
            db.add(invoice)
            db.flush()
            for det in payload.detalles:
                if not db.query(ConceptoCobro).filter(ConceptoCobro.id == det.concepto_id, ConceptoCobro.estado == "activo").first():
                    raise HTTPException(status_code=404, detail=f"Concepto no encontrado o inactivo: {det.concepto_id}")
                subtotal_linea = det.cantidad * det.valor_unitario
                subtotal += subtotal_linea
                db.add(
                    FacturaDetalle(
                        factura_id=invoice.id,
                        concepto_id=det.concepto_id,
                        descripcion=det.descripcion,
                        cantidad=det.cantidad,
                        valor_unitario=det.valor_unitario,
                        subtotal_linea=subtotal_linea,
                    )
                )
            invoice.subtotal = subtotal
            invoice.valor_impuesto = subtotal * (payload.porcentaje_impuesto / 100)
            invoice.total = invoice.subtotal + invoice.valor_impuesto
            _sync_estado_cuenta(db, payload.usuario_id)
            db.commit()
            db.refresh(invoice)
            return build_success_response(data={"id": invoice.id, "numero_factura": invoice.numero_factura, "total": float(invoice.total)}, message="Factura creada")


        @router.get("/facturas")
        def list_invoices(db: Session = Depends(get_db)):
            rows = db.query(Factura).order_by(Factura.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "numero_factura": x.numero_factura,
                    "usuario_id": x.usuario_id,
                    "fecha_emision": x.fecha_emision.isoformat() if x.fecha_emision else None,
                    "fecha_vencimiento": x.fecha_vencimiento.isoformat() if x.fecha_vencimiento else None,
                    "subtotal": float(x.subtotal),
                    "porcentaje_impuesto": float(x.porcentaje_impuesto),
                    "valor_impuesto": float(x.valor_impuesto),
                    "total": float(x.total),
                    "estado": x.estado,
                    "fecha_pago": x.fecha_pago.isoformat() if x.fecha_pago else None,
                    "observaciones": x.observaciones,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Facturas listadas")


        @router.put("/facturas/{factura_id}")
        def update_invoice(factura_id: int, observaciones: str, db: Session = Depends(get_db)):
            row = db.query(Factura).filter(Factura.id == factura_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Factura no encontrada")
            if row.estado != "emitida":
                raise HTTPException(status_code=409, detail="Solo se puede modificar factura emitida")
            row.observaciones = observaciones
            db.commit()
            return build_success_response(data={"id": factura_id}, message="Factura actualizada")


        @router.post("/facturas/{factura_id}/pagar")
        def pay_invoice(factura_id: int, db: Session = Depends(get_db)):
            row = db.query(Factura).filter(Factura.id == factura_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Factura no encontrada")
            if row.estado in {"pagada", "anulada"}:
                raise HTTPException(status_code=409, detail="Factura no pagable")
            row.estado = "pagada"
            row.fecha_pago = datetime.utcnow()
            _sync_estado_cuenta(db, row.usuario_id)
            db.commit()
            return build_success_response(data={"id": factura_id, "estado": row.estado}, message="Factura pagada")


        @router.post("/facturas/{factura_id}/anular")
        def cancel_invoice(factura_id: int, db: Session = Depends(get_db)):
            row = db.query(Factura).filter(Factura.id == factura_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Factura no encontrada")
            if row.estado == "pagada":
                raise HTTPException(status_code=409, detail="No se puede anular factura pagada")
            row.estado = "anulada"
            _sync_estado_cuenta(db, row.usuario_id)
            db.commit()
            return build_success_response(data={"id": factura_id, "estado": row.estado}, message="Factura anulada")


        @router.post("/facturas/actualizar-vencidas")
        def update_overdue(db: Session = Depends(get_db)):
            now = datetime.utcnow()
            rows = db.query(Factura).filter(Factura.estado == "emitida", Factura.fecha_vencimiento < now).all()
            impacted_users = set()
            for row in rows:
                row.estado = "vencida"
                impacted_users.add(row.usuario_id)
            for user_id in impacted_users:
                _sync_estado_cuenta(db, user_id)
            db.commit()
            return build_success_response(data={"facturas_actualizadas": len(rows)}, message="Facturas vencidas actualizadas")


        @router.get("/estado-cuenta/{usuario_id}")
        def account_status(usuario_id: int, db: Session = Depends(get_db)):
            _sync_estado_cuenta(db, usuario_id)
            db.commit()
            row = db.query(EstadoCuenta).filter(EstadoCuenta.usuario_id == usuario_id).first()
            if not row:
                return build_success_response(data={"usuario_id": usuario_id, "total_facturado": 0, "total_pagado": 0, "saldo_pendiente": 0, "facturas_vencidas": 0}, message="Estado de cuenta")
            data = {
                "usuario_id": row.usuario_id,
                "total_facturado": float(row.total_facturado),
                "total_pagado": float(row.total_pagado),
                "saldo_pendiente": float(row.saldo_pendiente),
                "facturas_vencidas": row.facturas_vencidas,
            }
            return build_success_response(data=data, message="Estado de cuenta")


        @router.post("/facturas/masivo/recurrente")
        def generate_massive_recurrent(concepto_id: int, usuario_ids: list[int], fecha_vencimiento: datetime, porcentaje_impuesto: float = 0, db: Session = Depends(get_db)):
            concepto = db.query(ConceptoCobro).filter(ConceptoCobro.id == concepto_id, ConceptoCobro.es_recurrente == True).first()  # noqa: E712
            if not concepto:
                raise HTTPException(status_code=404, detail="Concepto recurrente no encontrado")
            created = []
            for user_id in usuario_ids:
                numero = _next_invoice_number(db)
                subtotal = float(concepto.valor_base)
                impuesto = subtotal * (porcentaje_impuesto / 100)
                total = subtotal + impuesto
                factura = Factura(
                    numero_factura=numero,
                    usuario_id=user_id,
                    fecha_vencimiento=fecha_vencimiento,
                    subtotal=subtotal,
                    porcentaje_impuesto=porcentaje_impuesto,
                    valor_impuesto=impuesto,
                    total=total,
                    estado="emitida",
                    observaciones=f"Generacion masiva concepto recurrente {concepto.nombre}",
                )
                db.add(factura)
                db.flush()
                db.add(
                    FacturaDetalle(
                        factura_id=factura.id,
                        concepto_id=concepto.id,
                        descripcion=concepto.descripcion,
                        cantidad=1,
                        valor_unitario=float(concepto.valor_base),
                        subtotal_linea=float(concepto.valor_base),
                    )
                )
                _sync_estado_cuenta(db, user_id)
                created.append({"factura_id": factura.id, "numero_factura": factura.numero_factura, "usuario_id": user_id, "total": total})
            db.commit()
            return build_success_response(data={"creadas": created}, message="Facturacion masiva recurrente ejecutada")
        """
    ),
)

print("Modulo financiero implementado: presupuesto, gastos, facturacion.")
