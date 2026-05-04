from pathlib import Path
from textwrap import dedent

ROOT = Path(r"c:\Users\jhons\Downloads\Microservicios")


def write(rel_path: str, content: str) -> None:
    file_path = ROOT / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


# ms-espacios
write(
    "ms-espacios/requirements.txt",
    dedent(
        """\
        fastapi==0.115.0
        uvicorn==0.30.6
        sqlalchemy==2.0.36
        psycopg[binary]==3.2.3
        pydantic==2.9.2
        pydantic-settings==2.6.0
        httpx==0.27.2
        """
    ),
)

write(
    "ms-espacios/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-espacios
        SERVICE_CODE=ESP
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_espacios
        INV_BASE_URL=http://localhost:8004
        """
    ),
)

write(
    "ms-espacios/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_espacios;
        \\c db_espacios

        CREATE TABLE IF NOT EXISTS esp_tipos_espacio (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(80) NOT NULL UNIQUE,
            descripcion TEXT,
            requiere_equipamiento_especial BOOLEAN NOT NULL DEFAULT FALSE,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS esp_espacios (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(40) NOT NULL UNIQUE,
            nombre VARCHAR(140) NOT NULL,
            tipo_espacio_id INTEGER NOT NULL REFERENCES esp_tipos_espacio(id),
            edificio VARCHAR(80) NOT NULL,
            piso INTEGER,
            capacidad_maxima INTEGER NOT NULL,
            estado VARCHAR(30) NOT NULL DEFAULT 'disponible',
            descripcion TEXT,
            fecha_registro TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS esp_equipamiento_espacios (
            id SERIAL PRIMARY KEY,
            espacio_id INTEGER NOT NULL REFERENCES esp_espacios(id),
            activo_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            fecha_asignacion TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS esp_mantenimientos (
            id SERIAL PRIMARY KEY,
            espacio_id INTEGER NOT NULL REFERENCES esp_espacios(id),
            descripcion TEXT NOT NULL,
            responsable_id INTEGER,
            costo_estimado NUMERIC(14,2),
            fecha_programada TIMESTAMP NOT NULL,
            fecha_ejecucion_real TIMESTAMP,
            estado VARCHAR(30) NOT NULL DEFAULT 'programado',
            observaciones TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS esp_historial_ocupacion (
            id SERIAL PRIMARY KEY,
            espacio_id INTEGER NOT NULL REFERENCES esp_espacios(id),
            fecha DATE NOT NULL,
            horas_ocupadas NUMERIC(6,2) NOT NULL,
            horas_disponibles NUMERIC(6,2) NOT NULL,
            porcentaje_uso NUMERIC(6,2) NOT NULL,
            periodo VARCHAR(40) NOT NULL
        );
        """
    ),
)

write(
    "ms-espacios/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-espacios"
            SERVICE_CODE: str = "ESP"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_espacios"
            INV_BASE_URL: str = "http://localhost:8004"
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)

write(
    "ms-espacios/app/models/entities.py",
    dedent(
        """\
        from datetime import date, datetime
        from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class TipoEspacio(Base):
            __tablename__ = "esp_tipos_espacio"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            requiere_equipamiento_especial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())


        class Espacio(Base):
            __tablename__ = "esp_espacios"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
            nombre: Mapped[str] = mapped_column(String(140), nullable=False)
            tipo_espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_tipos_espacio.id"), nullable=False)
            edificio: Mapped[str] = mapped_column(String(80), nullable=False)
            piso: Mapped[int | None] = mapped_column(Integer, nullable=True)
            capacidad_maxima: Mapped[int] = mapped_column(Integer, nullable=False)
            estado: Mapped[str] = mapped_column(String(30), default="disponible", nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class EquipamientoEspacio(Base):
            __tablename__ = "esp_equipamiento_espacios"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_espacios.id"), nullable=False, index=True)
            activo_id: Mapped[int] = mapped_column(Integer, nullable=False)
            cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
            fecha_asignacion: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())


        class Mantenimiento(Base):
            __tablename__ = "esp_mantenimientos"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_espacios.id"), nullable=False, index=True)
            descripcion: Mapped[str] = mapped_column(Text, nullable=False)
            responsable_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
            costo_estimado: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
            fecha_programada: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
            fecha_ejecucion_real: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
            estado: Mapped[str] = mapped_column(String(30), default="programado", nullable=False)
            observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class HistorialOcupacion(Base):
            __tablename__ = "esp_historial_ocupacion"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            espacio_id: Mapped[int] = mapped_column(ForeignKey("esp_espacios.id"), nullable=False, index=True)
            fecha: Mapped[date] = mapped_column(Date, nullable=False)
            horas_ocupadas: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
            horas_disponibles: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
            porcentaje_uso: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
            periodo: Mapped[str] = mapped_column(String(40), nullable=False)
        """
    ),
)

write(
    "ms-espacios/app/schemas/entities.py",
    dedent(
        """\
        from datetime import date, datetime
        from pydantic import BaseModel, ConfigDict


        class TipoEspacioIn(BaseModel):
            nombre: str
            descripcion: str | None = None
            requiere_equipamiento_especial: bool = False
            estado: str = "activo"


        class TipoEspacioOut(TipoEspacioIn):
            id: int
            created_at: datetime | None = None
            model_config = ConfigDict(from_attributes=True)


        class EspacioIn(BaseModel):
            codigo: str
            nombre: str
            tipo_espacio_id: int
            edificio: str
            piso: int | None = None
            capacidad_maxima: int
            estado: str = "disponible"
            descripcion: str | None = None


        class EspacioUpdate(BaseModel):
            nombre: str | None = None
            tipo_espacio_id: int | None = None
            edificio: str | None = None
            piso: int | None = None
            capacidad_maxima: int | None = None
            estado: str | None = None
            descripcion: str | None = None


        class EspacioOut(EspacioIn):
            id: int
            fecha_registro: datetime | None = None
            updated_at: datetime | None = None
            model_config = ConfigDict(from_attributes=True)


        class EstadoEspacioIn(BaseModel):
            estado: str
            motivo: str
            changed_by: int | None = None


        class EquipamientoIn(BaseModel):
            espacio_id: int
            activo_id: int
            cantidad: int


        class MantenimientoIn(BaseModel):
            espacio_id: int
            descripcion: str
            responsable_id: int | None = None
            costo_estimado: float | None = None
            fecha_programada: datetime
            estado: str = "programado"
            observaciones: str | None = None


        class MantenimientoUpdate(BaseModel):
            descripcion: str | None = None
            responsable_id: int | None = None
            costo_estimado: float | None = None
            fecha_programada: datetime | None = None
            fecha_ejecucion_real: datetime | None = None
            estado: str | None = None
            observaciones: str | None = None


        class OcupacionIn(BaseModel):
            espacio_id: int
            fecha: date
            horas_ocupadas: float
            horas_disponibles: float
            periodo: str
        """
    ),
)

write(
    "ms-espacios/app/api/routes/entities.py",
    dedent(
        """\
        import httpx
        from fastapi import APIRouter, Depends, HTTPException, Query
        from sqlalchemy.orm import Session

        from app.core.config import settings
        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import EquipamientoEspacio, Espacio, HistorialOcupacion, Mantenimiento, TipoEspacio
        from app.schemas.entities import (
            EquipamientoIn,
            EspacioIn,
            EspacioOut,
            EspacioUpdate,
            EstadoEspacioIn,
            MantenimientoIn,
            MantenimientoUpdate,
            OcupacionIn,
            TipoEspacioIn,
            TipoEspacioOut,
        )

        router = APIRouter(tags=["ms-espacios"])


        async def _validate_activo(activo_id: int) -> None:
            async with httpx.AsyncClient(timeout=4.0) as client:
                r = await client.get(f"{settings.INV_BASE_URL}/api/v1/activos/{activo_id}")
                if r.status_code >= 400:
                    raise HTTPException(status_code=404, detail="Activo no encontrado en inventario")


        @router.post("/tipos-espacio")
        def create_tipo(payload: TipoEspacioIn, db: Session = Depends(get_db)):
            if db.query(TipoEspacio).filter(TipoEspacio.nombre == payload.nombre).first():
                raise HTTPException(status_code=409, detail="Tipo de espacio ya existe")
            row = TipoEspacio(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data=TipoEspacioOut.model_validate(row).model_dump(mode="json"), message="Tipo creado")


        @router.get("/tipos-espacio")
        def list_tipos(db: Session = Depends(get_db)):
            rows = db.query(TipoEspacio).order_by(TipoEspacio.nombre.asc()).all()
            data = [TipoEspacioOut.model_validate(x).model_dump(mode="json") for x in rows]
            return build_success_response(data=data, message="Tipos listados")


        @router.post("/espacios")
        def create_space(payload: EspacioIn, db: Session = Depends(get_db)):
            if not db.query(TipoEspacio).filter(TipoEspacio.id == payload.tipo_espacio_id).first():
                raise HTTPException(status_code=404, detail="Tipo de espacio no existe")
            if db.query(Espacio).filter(Espacio.codigo == payload.codigo).first():
                raise HTTPException(status_code=409, detail="Codigo de espacio duplicado")
            row = Espacio(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data=EspacioOut.model_validate(row).model_dump(mode="json"), message="Espacio creado")


        @router.get("/espacios")
        def list_spaces(db: Session = Depends(get_db)):
            rows = db.query(Espacio).order_by(Espacio.id.desc()).all()
            data = [EspacioOut.model_validate(x).model_dump(mode="json") for x in rows]
            return build_success_response(data=data, message="Espacios listados")


        @router.get("/espacios/{espacio_id}")
        def get_space(espacio_id: int, db: Session = Depends(get_db)):
            row = db.query(Espacio).filter(Espacio.id == espacio_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Espacio no encontrado")
            return build_success_response(data=EspacioOut.model_validate(row).model_dump(mode="json"), message="Espacio consultado")


        @router.put("/espacios/{espacio_id}")
        def update_space(espacio_id: int, payload: EspacioUpdate, db: Session = Depends(get_db)):
            row = db.query(Espacio).filter(Espacio.id == espacio_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Espacio no encontrado")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            db.commit()
            db.refresh(row)
            return build_success_response(data=EspacioOut.model_validate(row).model_dump(mode="json"), message="Espacio actualizado")


        @router.post("/espacios/{espacio_id}/estado")
        def change_space_state(espacio_id: int, payload: EstadoEspacioIn, db: Session = Depends(get_db)):
            row = db.query(Espacio).filter(Espacio.id == espacio_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Espacio no encontrado")
            row.estado = payload.estado
            db.commit()
            return build_success_response(
                data={"espacio_id": espacio_id, "estado": payload.estado, "motivo": payload.motivo, "changed_by": payload.changed_by},
                message="Estado del espacio actualizado",
            )


        @router.get("/espacios/disponibles")
        def find_available_spaces(
            tipo_espacio_id: int | None = Query(default=None),
            capacidad_minima: int | None = Query(default=None),
            edificio: str | None = Query(default=None),
            estado: str = Query(default="disponible"),
            db: Session = Depends(get_db),
        ):
            query = db.query(Espacio).filter(Espacio.estado == estado)
            if tipo_espacio_id:
                query = query.filter(Espacio.tipo_espacio_id == tipo_espacio_id)
            if capacidad_minima:
                query = query.filter(Espacio.capacidad_maxima >= capacidad_minima)
            if edificio:
                query = query.filter(Espacio.edificio.ilike(f"%{edificio}%"))
            rows = query.order_by(Espacio.capacidad_maxima.asc()).all()
            data = [EspacioOut.model_validate(x).model_dump(mode="json") for x in rows]
            return build_success_response(data=data, message="Busqueda de espacios disponible")


        @router.post("/equipamiento/asignar")
        async def assign_equipment(payload: EquipamientoIn, db: Session = Depends(get_db)):
            espacio = db.query(Espacio).filter(Espacio.id == payload.espacio_id).first()
            if not espacio:
                raise HTTPException(status_code=404, detail="Espacio no encontrado")
            await _validate_activo(payload.activo_id)
            existing = db.query(EquipamientoEspacio).filter(
                EquipamientoEspacio.espacio_id == payload.espacio_id,
                EquipamientoEspacio.activo_id == payload.activo_id,
                EquipamientoEspacio.estado == "activo",
            ).first()
            if existing:
                existing.cantidad += payload.cantidad
                db.commit()
                return build_success_response(data={"id": existing.id, "cantidad": existing.cantidad}, message="Equipamiento actualizado")
            row = EquipamientoEspacio(**payload.model_dump(), estado="activo")
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Equipamiento asignado")


        @router.delete("/equipamiento/remover")
        def remove_equipment(espacio_id: int, activo_id: int, db: Session = Depends(get_db)):
            row = db.query(EquipamientoEspacio).filter(
                EquipamientoEspacio.espacio_id == espacio_id,
                EquipamientoEspacio.activo_id == activo_id,
                EquipamientoEspacio.estado == "activo",
            ).first()
            if not row:
                raise HTTPException(status_code=404, detail="Asignacion de equipamiento no encontrada")
            row.estado = "inactivo"
            db.commit()
            return build_success_response(data={"espacio_id": espacio_id, "activo_id": activo_id}, message="Equipamiento removido")


        @router.get("/espacios/{espacio_id}/equipamiento")
        def list_equipment(espacio_id: int, db: Session = Depends(get_db)):
            rows = db.query(EquipamientoEspacio).filter(
                EquipamientoEspacio.espacio_id == espacio_id,
                EquipamientoEspacio.estado == "activo",
            ).all()
            data = [{"id": x.id, "activo_id": x.activo_id, "cantidad": x.cantidad, "fecha_asignacion": x.fecha_asignacion.isoformat() if x.fecha_asignacion else None} for x in rows]
            return build_success_response(data=data, message="Equipamiento del espacio")


        @router.post("/mantenimientos")
        def create_maintenance(payload: MantenimientoIn, db: Session = Depends(get_db)):
            space = db.query(Espacio).filter(Espacio.id == payload.espacio_id).first()
            if not space:
                raise HTTPException(status_code=404, detail="Espacio no encontrado")
            row = Mantenimiento(**payload.model_dump())
            db.add(row)
            space.estado = "en mantenimiento"
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Mantenimiento programado")


        @router.get("/mantenimientos")
        def list_maintenances(db: Session = Depends(get_db)):
            rows = db.query(Mantenimiento).order_by(Mantenimiento.fecha_programada.desc()).all()
            data = [
                {
                    "id": x.id,
                    "espacio_id": x.espacio_id,
                    "descripcion": x.descripcion,
                    "responsable_id": x.responsable_id,
                    "costo_estimado": float(x.costo_estimado) if x.costo_estimado is not None else None,
                    "fecha_programada": x.fecha_programada.isoformat() if x.fecha_programada else None,
                    "fecha_ejecucion_real": x.fecha_ejecucion_real.isoformat() if x.fecha_ejecucion_real else None,
                    "estado": x.estado,
                    "observaciones": x.observaciones,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Mantenimientos listados")


        @router.put("/mantenimientos/{mantenimiento_id}")
        def update_maintenance(mantenimiento_id: int, payload: MantenimientoUpdate, db: Session = Depends(get_db)):
            row = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            space = db.query(Espacio).filter(Espacio.id == row.espacio_id).first()
            if payload.estado == "completado" and space:
                space.estado = "disponible"
            elif payload.estado in {"programado", "en ejecucion"} and space:
                space.estado = "en mantenimiento"
            db.commit()
            return build_success_response(data={"id": mantenimiento_id}, message="Mantenimiento actualizado")


        @router.post("/ocupacion")
        def create_occupation(payload: OcupacionIn, db: Session = Depends(get_db)):
            if not db.query(Espacio).filter(Espacio.id == payload.espacio_id).first():
                raise HTTPException(status_code=404, detail="Espacio no encontrado")
            if payload.horas_disponibles <= 0:
                raise HTTPException(status_code=400, detail="Horas disponibles deben ser mayores a cero")
            porcentaje = round((payload.horas_ocupadas / payload.horas_disponibles) * 100, 2)
            row = HistorialOcupacion(
                espacio_id=payload.espacio_id,
                fecha=payload.fecha,
                horas_ocupadas=payload.horas_ocupadas,
                horas_disponibles=payload.horas_disponibles,
                porcentaje_uso=porcentaje,
                periodo=payload.periodo,
            )
            db.add(row)
            db.commit()
            return build_success_response(data={"id": row.id, "porcentaje_uso": porcentaje}, message="Ocupacion registrada")


        @router.get("/espacios/{espacio_id}/ocupacion")
        def occupation_stats(espacio_id: int, periodo: str | None = None, db: Session = Depends(get_db)):
            query = db.query(HistorialOcupacion).filter(HistorialOcupacion.espacio_id == espacio_id)
            if periodo:
                query = query.filter(HistorialOcupacion.periodo == periodo)
            rows = query.order_by(HistorialOcupacion.fecha.desc()).all()
            data = [
                {
                    "fecha": x.fecha.isoformat() if x.fecha else None,
                    "horas_ocupadas": float(x.horas_ocupadas),
                    "horas_disponibles": float(x.horas_disponibles),
                    "porcentaje_uso": float(x.porcentaje_uso),
                    "periodo": x.periodo,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Estadisticas de ocupacion")
        """
    ),
)


# ms-reservas
write(
    "ms-reservas/requirements.txt",
    dedent(
        """\
        fastapi==0.115.0
        uvicorn==0.30.6
        sqlalchemy==2.0.36
        psycopg[binary]==3.2.3
        pydantic==2.9.2
        pydantic-settings==2.6.0
        httpx==0.27.2
        """
    ),
)

write(
    "ms-reservas/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-reservas
        SERVICE_CODE=RES
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_reservas
        ESP_BASE_URL=http://localhost:8005
        HOR_BASE_URL=http://localhost:8016
        """
    ),
)

write(
    "ms-reservas/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_reservas;
        \\c db_reservas

        CREATE TABLE IF NOT EXISTS res_reservas (
            id SERIAL PRIMARY KEY,
            espacio_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            titulo VARCHAR(180) NOT NULL,
            descripcion TEXT,
            fecha_inicio TIMESTAMP NOT NULL,
            fecha_fin TIMESTAMP NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            cancelled_by INTEGER,
            motivo_cancelacion TEXT,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS res_politicas (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL UNIQUE,
            min_anticipacion_horas INTEGER NOT NULL,
            max_anticipacion_dias INTEGER NOT NULL,
            duracion_max_horas INTEGER NOT NULL,
            limite_cancelacion_horas INTEGER NOT NULL,
            max_reservas_activas_usuario INTEGER NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo'
        );

        CREATE TABLE IF NOT EXISTS res_bloqueos_espacio (
            id SERIAL PRIMARY KEY,
            espacio_id INTEGER NOT NULL,
            fecha_inicio TIMESTAMP NOT NULL,
            fecha_fin TIMESTAMP NOT NULL,
            motivo TEXT NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)

write(
    "ms-reservas/app/core/config.py",
    dedent(
        """\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            PROJECT_NAME: str = "ms-reservas"
            SERVICE_CODE: str = "RES"
            API_V1_STR: str = "/api/v1"
            DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/db_reservas"
            ESP_BASE_URL: str = "http://localhost:8005"
            HOR_BASE_URL: str = "http://localhost:8016"
            model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


        settings = Settings()
        """
    ),
)

write(
    "ms-reservas/app/models/entities.py",
    dedent(
        """\
        from datetime import datetime
        from sqlalchemy import DateTime, Integer, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class Reserva(Base):
            __tablename__ = "res_reservas"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            espacio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            titulo: Mapped[str] = mapped_column(String(180), nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
            fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            cancelled_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
            motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class PoliticaReserva(Base):
            __tablename__ = "res_politicas"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
            min_anticipacion_horas: Mapped[int] = mapped_column(Integer, nullable=False)
            max_anticipacion_dias: Mapped[int] = mapped_column(Integer, nullable=False)
            duracion_max_horas: Mapped[int] = mapped_column(Integer, nullable=False)
            limite_cancelacion_horas: Mapped[int] = mapped_column(Integer, nullable=False)
            max_reservas_activas_usuario: Mapped[int] = mapped_column(Integer, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)


        class BloqueoEspacio(Base):
            __tablename__ = "res_bloqueos_espacio"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            espacio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
            fecha_fin: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
            motivo: Mapped[str] = mapped_column(Text, nullable=False)
            created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
        """
    ),
)

write(
    "ms-reservas/app/schemas/entities.py",
    dedent(
        """\
        from datetime import datetime
        from pydantic import BaseModel, ConfigDict


        class ReservaIn(BaseModel):
            espacio_id: int
            usuario_id: int
            titulo: str
            descripcion: str | None = None
            fecha_inicio: datetime
            fecha_fin: datetime


        class ReservaUpdate(BaseModel):
            titulo: str | None = None
            descripcion: str | None = None
            fecha_inicio: datetime | None = None
            fecha_fin: datetime | None = None


        class CancelReservaIn(BaseModel):
            motivo: str
            cancelled_by: int | None = None


        class ReservaOut(BaseModel):
            id: int
            espacio_id: int
            usuario_id: int
            titulo: str
            descripcion: str | None = None
            fecha_inicio: datetime
            fecha_fin: datetime
            estado: str
            created_at: datetime | None = None
            cancelled_by: int | None = None
            motivo_cancelacion: str | None = None
            updated_at: datetime | None = None
            model_config = ConfigDict(from_attributes=True)


        class PoliticaIn(BaseModel):
            nombre: str
            min_anticipacion_horas: int
            max_anticipacion_dias: int
            duracion_max_horas: int
            limite_cancelacion_horas: int
            max_reservas_activas_usuario: int
            estado: str = "activo"


        class BloqueoIn(BaseModel):
            espacio_id: int
            fecha_inicio: datetime
            fecha_fin: datetime
            motivo: str
            created_by: int | None = None
        """
    ),
)

write(
    "ms-reservas/app/db/init_db.py",
    dedent(
        """\
        from app.db.session import Base, SessionLocal, engine
        from app.models.entities import BloqueoEspacio, PoliticaReserva, Reserva  # noqa: F401


        def init_db() -> None:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                if not db.query(PoliticaReserva).filter(PoliticaReserva.nombre == "Politica General").first():
                    db.add(
                        PoliticaReserva(
                            nombre="Politica General",
                            min_anticipacion_horas=2,
                            max_anticipacion_dias=60,
                            duracion_max_horas=8,
                            limite_cancelacion_horas=1,
                            max_reservas_activas_usuario=3,
                            estado="activo",
                        )
                    )
                    db.commit()
            finally:
                db.close()
        """
    ),
)

write(
    "ms-reservas/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import datetime

        import httpx
        from fastapi import APIRouter, Depends, HTTPException, Query
        from sqlalchemy import and_, func, or_
        from sqlalchemy.orm import Session

        from app.core.config import settings
        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import BloqueoEspacio, PoliticaReserva, Reserva
        from app.schemas.entities import BloqueoIn, CancelReservaIn, PoliticaIn, ReservaIn, ReservaOut, ReservaUpdate

        router = APIRouter(tags=["ms-reservas"])


        def _policy(db: Session) -> PoliticaReserva:
            row = db.query(PoliticaReserva).filter(PoliticaReserva.estado == "activo").order_by(PoliticaReserva.id.desc()).first()
            if not row:
                raise HTTPException(status_code=400, detail="No existe politica activa")
            return row


        async def _validate_space(espacio_id: int) -> dict:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(f"{settings.ESP_BASE_URL}/api/v1/espacios/{espacio_id}")
                if resp.status_code >= 400:
                    raise HTTPException(status_code=404, detail="Espacio no encontrado")
                data = resp.json()["data"]
                if data["estado"] not in {"disponible", "reservado"}:
                    raise HTTPException(status_code=409, detail="Espacio no disponible para reserva")
                return data


        async def _validate_with_horarios(espacio_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> None:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(
                    f"{settings.HOR_BASE_URL}/api/v1/franjas/conflicto-espacio",
                    params={"espacio_id": espacio_id, "fecha_inicio": fecha_inicio.isoformat(), "fecha_fin": fecha_fin.isoformat()},
                )
                if resp.status_code == 404:
                    return
                if resp.status_code >= 400:
                    raise HTTPException(status_code=503, detail="No fue posible validar conflicto con ms-horarios")
                conflicto = resp.json().get("data", {}).get("conflicto", False)
                if conflicto:
                    raise HTTPException(status_code=409, detail="Conflicto con horario academico")


        def _has_overlap(query, fecha_inicio: datetime, fecha_fin: datetime):
            return query.filter(
                and_(
                    Reserva.fecha_inicio < fecha_fin,
                    Reserva.fecha_fin > fecha_inicio,
                )
            ).first()


        @router.post("/reservas")
        async def create_reserva(payload: ReservaIn, db: Session = Depends(get_db)):
            await _validate_space(payload.espacio_id)
            await _validate_with_horarios(payload.espacio_id, payload.fecha_inicio, payload.fecha_fin)
            pol = _policy(db)
            if payload.fecha_fin <= payload.fecha_inicio:
                raise HTTPException(status_code=400, detail="Rango de fechas invalido")
            delta_hours = (payload.fecha_fin - payload.fecha_inicio).total_seconds() / 3600
            if delta_hours > pol.duracion_max_horas:
                raise HTTPException(status_code=409, detail="La reserva supera la duracion maxima permitida")
            hours_until_start = (payload.fecha_inicio - datetime.utcnow()).total_seconds() / 3600
            if hours_until_start < pol.min_anticipacion_horas:
                raise HTTPException(status_code=409, detail="No cumple anticipacion minima")
            if hours_until_start > pol.max_anticipacion_dias * 24:
                raise HTTPException(status_code=409, detail="Supera anticipacion maxima")

            active_count = db.query(func.count(Reserva.id)).filter(
                Reserva.usuario_id == payload.usuario_id,
                Reserva.estado.in_(["pendiente", "confirmada"]),
            ).scalar() or 0
            if active_count >= pol.max_reservas_activas_usuario:
                raise HTTPException(status_code=409, detail="El usuario excede reservas activas permitidas")

            overlap = _has_overlap(
                db.query(Reserva).filter(
                    Reserva.espacio_id == payload.espacio_id,
                    Reserva.estado.in_(["pendiente", "confirmada"]),
                ),
                payload.fecha_inicio,
                payload.fecha_fin,
            )
            if overlap:
                raise HTTPException(status_code=409, detail="Conflicto de horario: espacio ya reservado")

            blocked = db.query(BloqueoEspacio).filter(
                BloqueoEspacio.espacio_id == payload.espacio_id,
                BloqueoEspacio.fecha_inicio < payload.fecha_fin,
                BloqueoEspacio.fecha_fin > payload.fecha_inicio,
            ).first()
            if blocked:
                raise HTTPException(status_code=409, detail="El espacio esta bloqueado en ese periodo")

            row = Reserva(**payload.model_dump(), estado="pendiente")
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data=ReservaOut.model_validate(row).model_dump(mode="json"), message="Reserva creada")


        @router.get("/reservas")
        def list_reservas(db: Session = Depends(get_db)):
            rows = db.query(Reserva).order_by(Reserva.id.desc()).all()
            data = [ReservaOut.model_validate(x).model_dump(mode="json") for x in rows]
            return build_success_response(data=data, message="Reservas listadas")


        @router.get("/reservas/{reserva_id}")
        def get_reserva(reserva_id: int, db: Session = Depends(get_db)):
            row = db.query(Reserva).filter(Reserva.id == reserva_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Reserva no encontrada")
            return build_success_response(data=ReservaOut.model_validate(row).model_dump(mode="json"), message="Reserva consultada")


        @router.put("/reservas/{reserva_id}")
        async def update_reserva(reserva_id: int, payload: ReservaUpdate, db: Session = Depends(get_db)):
            row = db.query(Reserva).filter(Reserva.id == reserva_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Reserva no encontrada")
            start = payload.fecha_inicio or row.fecha_inicio
            end = payload.fecha_fin or row.fecha_fin
            await _validate_with_horarios(row.espacio_id, start, end)
            overlap = _has_overlap(
                db.query(Reserva).filter(
                    Reserva.espacio_id == row.espacio_id,
                    Reserva.id != reserva_id,
                    Reserva.estado.in_(["pendiente", "confirmada"]),
                ),
                start,
                end,
            )
            if overlap:
                raise HTTPException(status_code=409, detail="Conflicto de horario en actualizacion")
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            db.commit()
            db.refresh(row)
            return build_success_response(data=ReservaOut.model_validate(row).model_dump(mode="json"), message="Reserva actualizada")


        @router.post("/reservas/{reserva_id}/confirmar")
        def confirm_reserva(reserva_id: int, db: Session = Depends(get_db)):
            row = db.query(Reserva).filter(Reserva.id == reserva_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Reserva no encontrada")
            row.estado = "confirmada"
            db.commit()
            db.refresh(row)
            return build_success_response(data=ReservaOut.model_validate(row).model_dump(mode="json"), message="Reserva confirmada")


        @router.post("/reservas/{reserva_id}/cancelar")
        def cancel_reserva(reserva_id: int, payload: CancelReservaIn, db: Session = Depends(get_db)):
            row = db.query(Reserva).filter(Reserva.id == reserva_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Reserva no encontrada")
            pol = _policy(db)
            hours_remaining = (row.fecha_inicio - datetime.utcnow()).total_seconds() / 3600
            if hours_remaining < pol.limite_cancelacion_horas:
                raise HTTPException(status_code=409, detail="La cancelacion esta fuera del limite permitido")
            row.estado = "cancelada"
            row.cancelled_by = payload.cancelled_by
            row.motivo_cancelacion = payload.motivo
            db.commit()
            db.refresh(row)
            return build_success_response(data=ReservaOut.model_validate(row).model_dump(mode="json"), message="Reserva cancelada")


        @router.get("/disponibilidad")
        def disponibilidad(espacio_id: int, fecha_inicio: datetime, fecha_fin: datetime, db: Session = Depends(get_db)):
            overlap = _has_overlap(
                db.query(Reserva).filter(
                    Reserva.espacio_id == espacio_id,
                    Reserva.estado.in_(["pendiente", "confirmada"]),
                ),
                fecha_inicio,
                fecha_fin,
            )
            blocked = db.query(BloqueoEspacio).filter(
                BloqueoEspacio.espacio_id == espacio_id,
                BloqueoEspacio.fecha_inicio < fecha_fin,
                BloqueoEspacio.fecha_fin > fecha_inicio,
            ).first()
            disponible = overlap is None and blocked is None
            return build_success_response(data={"disponible": disponible}, message="Disponibilidad calculada")


        @router.post("/politicas")
        def create_policy(payload: PoliticaIn, db: Session = Depends(get_db)):
            if db.query(PoliticaReserva).filter(PoliticaReserva.nombre == payload.nombre).first():
                raise HTTPException(status_code=409, detail="Politica duplicada")
            row = PoliticaReserva(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Politica creada")


        @router.get("/politicas")
        def list_policies(db: Session = Depends(get_db)):
            rows = db.query(PoliticaReserva).order_by(PoliticaReserva.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "nombre": x.nombre,
                    "min_anticipacion_horas": x.min_anticipacion_horas,
                    "max_anticipacion_dias": x.max_anticipacion_dias,
                    "duracion_max_horas": x.duracion_max_horas,
                    "limite_cancelacion_horas": x.limite_cancelacion_horas,
                    "max_reservas_activas_usuario": x.max_reservas_activas_usuario,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Politicas listadas")


        @router.put("/politicas/{politica_id}")
        def update_policy(politica_id: int, payload: PoliticaIn, db: Session = Depends(get_db)):
            row = db.query(PoliticaReserva).filter(PoliticaReserva.id == politica_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Politica no encontrada")
            for key, value in payload.model_dump().items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": politica_id}, message="Politica actualizada")


        @router.post("/bloqueos")
        def create_block(payload: BloqueoIn, db: Session = Depends(get_db)):
            if payload.fecha_fin <= payload.fecha_inicio:
                raise HTTPException(status_code=400, detail="Rango de bloqueo invalido")
            row = BloqueoEspacio(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Bloqueo creado")


        @router.get("/bloqueos")
        def list_blocks(db: Session = Depends(get_db)):
            rows = db.query(BloqueoEspacio).order_by(BloqueoEspacio.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "espacio_id": x.espacio_id,
                    "fecha_inicio": x.fecha_inicio.isoformat() if x.fecha_inicio else None,
                    "fecha_fin": x.fecha_fin.isoformat() if x.fecha_fin else None,
                    "motivo": x.motivo,
                    "created_by": x.created_by,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Bloqueos listados")


        @router.delete("/bloqueos/{bloqueo_id}")
        def delete_block(bloqueo_id: int, db: Session = Depends(get_db)):
            row = db.query(BloqueoEspacio).filter(BloqueoEspacio.id == bloqueo_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Bloqueo no encontrado")
            db.delete(row)
            db.commit()
            return build_success_response(data={"id": bloqueo_id}, message="Bloqueo eliminado")
        """
    ),
)

print("ms-espacios y ms-reservas implementados.")
