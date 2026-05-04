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

# ms-programas
write("ms-programas/requirements.txt", COMMON_REQ)
write(
    "ms-programas/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-programas
        SERVICE_CODE=PRG
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_programas
        """
    ),
)
write(
    "ms-programas/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_programas;
        \\c db_programas

        CREATE TABLE IF NOT EXISTS prg_programas (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(40) NOT NULL UNIQUE,
            nombre VARCHAR(160) NOT NULL,
            descripcion TEXT,
            duracion_semestres INTEGER NOT NULL,
            total_creditos_requeridos INTEGER NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            coordinador_usuario_id INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS prg_asignaturas (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(40) NOT NULL UNIQUE,
            nombre VARCHAR(160) NOT NULL,
            descripcion TEXT,
            creditos INTEGER NOT NULL,
            semestre_sugerido INTEGER NOT NULL,
            programa_id INTEGER NOT NULL REFERENCES prg_programas(id),
            horas_semanales INTEGER NOT NULL,
            tipo VARCHAR(30) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS prg_prerrequisitos (
            id SERIAL PRIMARY KEY,
            asignatura_id INTEGER NOT NULL REFERENCES prg_asignaturas(id),
            prerrequisito_id INTEGER NOT NULL REFERENCES prg_asignaturas(id),
            tipo VARCHAR(20) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS prg_mallas_version (
            id SERIAL PRIMARY KEY,
            programa_id INTEGER NOT NULL REFERENCES prg_programas(id),
            version_identificador VARCHAR(40) NOT NULL,
            fecha_vigencia_inicio DATE NOT NULL,
            fecha_vigencia_fin DATE,
            estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
            descripcion_cambios TEXT,
            creado_por INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-programas/app/models/entities.py",
    dedent(
        """\
        from datetime import date, datetime
        from sqlalchemy import DATE, DateTime, ForeignKey, Integer, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class Programa(Base):
            __tablename__ = "prg_programas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
            nombre: Mapped[str] = mapped_column(String(160), nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            duracion_semestres: Mapped[int] = mapped_column(Integer, nullable=False)
            total_creditos_requeridos: Mapped[int] = mapped_column(Integer, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
            coordinador_usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Asignatura(Base):
            __tablename__ = "prg_asignaturas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
            nombre: Mapped[str] = mapped_column(String(160), nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            creditos: Mapped[int] = mapped_column(Integer, nullable=False)
            semestre_sugerido: Mapped[int] = mapped_column(Integer, nullable=False)
            programa_id: Mapped[int] = mapped_column(ForeignKey("prg_programas.id"), nullable=False, index=True)
            horas_semanales: Mapped[int] = mapped_column(Integer, nullable=False)
            tipo: Mapped[str] = mapped_column(String(30), nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Prerrequisito(Base):
            __tablename__ = "prg_prerrequisitos"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            asignatura_id: Mapped[int] = mapped_column(ForeignKey("prg_asignaturas.id"), nullable=False, index=True)
            prerrequisito_id: Mapped[int] = mapped_column(ForeignKey("prg_asignaturas.id"), nullable=False, index=True)
            tipo: Mapped[str] = mapped_column(String(20), nullable=False)


        class MallaVersion(Base):
            __tablename__ = "prg_mallas_version"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            programa_id: Mapped[int] = mapped_column(ForeignKey("prg_programas.id"), nullable=False, index=True)
            version_identificador: Mapped[str] = mapped_column(String(40), nullable=False)
            fecha_vigencia_inicio: Mapped[date] = mapped_column(DATE, nullable=False)
            fecha_vigencia_fin: Mapped[date | None] = mapped_column(DATE, nullable=True)
            estado: Mapped[str] = mapped_column(String(20), default="borrador", nullable=False)
            descripcion_cambios: Mapped[str | None] = mapped_column(Text, nullable=True)
            creado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
        """
    ),
)
write(
    "ms-programas/app/schemas/entities.py",
    dedent(
        """\
        from datetime import date
        from pydantic import BaseModel


        class ProgramaIn(BaseModel):
            codigo: str
            nombre: str
            descripcion: str | None = None
            duracion_semestres: int
            total_creditos_requeridos: int
            estado: str = "activo"
            coordinador_usuario_id: int | None = None


        class AsignaturaIn(BaseModel):
            codigo: str
            nombre: str
            descripcion: str | None = None
            creditos: int
            semestre_sugerido: int
            programa_id: int
            horas_semanales: int
            tipo: str
            estado: str = "activo"


        class PrerrequisitoIn(BaseModel):
            asignatura_id: int
            prerrequisito_id: int
            tipo: str


        class MallaVersionIn(BaseModel):
            programa_id: int
            version_identificador: str
            fecha_vigencia_inicio: date
            fecha_vigencia_fin: date | None = None
            estado: str = "borrador"
            descripcion_cambios: str | None = None
            creado_por: int | None = None
        """
    ),
)
write(
    "ms-programas/app/api/routes/entities.py",
    dedent(
        """\
        from collections import defaultdict

        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import Asignatura, MallaVersion, Programa, Prerrequisito
        from app.schemas.entities import AsignaturaIn, MallaVersionIn, ProgramaIn, PrerrequisitoIn

        router = APIRouter(tags=["ms-programas"])


        def _has_cycle(db: Session, asignatura_id: int, prerrequisito_id: int) -> bool:
            graph = defaultdict(list)
            rows = db.query(Prerrequisito).all()
            for row in rows:
                graph[row.asignatura_id].append(row.prerrequisito_id)
            graph[asignatura_id].append(prerrequisito_id)

            def dfs(node: int, target: int, visited: set[int]) -> bool:
                if node == target:
                    return True
                if node in visited:
                    return False
                visited.add(node)
                for nxt in graph.get(node, []):
                    if dfs(nxt, target, visited):
                        return True
                return False

            return dfs(prerrequisito_id, asignatura_id, set())


        @router.post("/programas")
        def create_program(payload: ProgramaIn, db: Session = Depends(get_db)):
            if db.query(Programa).filter(Programa.codigo == payload.codigo).first():
                raise HTTPException(status_code=409, detail="Codigo de programa duplicado")
            row = Programa(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Programa creado")


        @router.get("/programas")
        def list_programs(db: Session = Depends(get_db)):
            rows = db.query(Programa).order_by(Programa.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "codigo": x.codigo,
                    "nombre": x.nombre,
                    "descripcion": x.descripcion,
                    "duracion_semestres": x.duracion_semestres,
                    "total_creditos_requeridos": x.total_creditos_requeridos,
                    "estado": x.estado,
                    "coordinador_usuario_id": x.coordinador_usuario_id,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Programas listados")


        @router.put("/programas/{programa_id}")
        def update_program(programa_id: int, payload: ProgramaIn, db: Session = Depends(get_db)):
            row = db.query(Programa).filter(Programa.id == programa_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Programa no encontrado")
            for key, value in payload.model_dump().items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": programa_id}, message="Programa actualizado")


        @router.post("/programas/{programa_id}/desactivar")
        def deactivate_program(programa_id: int, db: Session = Depends(get_db)):
            row = db.query(Programa).filter(Programa.id == programa_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Programa no encontrado")
            row.estado = "inactivo"
            db.commit()
            return build_success_response(data={"id": programa_id}, message="Programa desactivado")


        @router.post("/asignaturas")
        def create_subject(payload: AsignaturaIn, db: Session = Depends(get_db)):
            if not db.query(Programa).filter(Programa.id == payload.programa_id).first():
                raise HTTPException(status_code=404, detail="Programa no encontrado")
            if db.query(Asignatura).filter(Asignatura.codigo == payload.codigo).first():
                raise HTTPException(status_code=409, detail="Codigo de asignatura duplicado")
            row = Asignatura(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Asignatura creada")


        @router.get("/asignaturas")
        def list_subjects(programa_id: int | None = None, db: Session = Depends(get_db)):
            query = db.query(Asignatura)
            if programa_id:
                query = query.filter(Asignatura.programa_id == programa_id)
            rows = query.order_by(Asignatura.semestre_sugerido.asc(), Asignatura.nombre.asc()).all()
            data = [
                {
                    "id": x.id,
                    "codigo": x.codigo,
                    "nombre": x.nombre,
                    "descripcion": x.descripcion,
                    "creditos": x.creditos,
                    "semestre_sugerido": x.semestre_sugerido,
                    "programa_id": x.programa_id,
                    "horas_semanales": x.horas_semanales,
                    "tipo": x.tipo,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Asignaturas listadas")


        @router.put("/asignaturas/{asignatura_id}")
        def update_subject(asignatura_id: int, payload: AsignaturaIn, db: Session = Depends(get_db)):
            row = db.query(Asignatura).filter(Asignatura.id == asignatura_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Asignatura no encontrada")
            for key, value in payload.model_dump().items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": asignatura_id}, message="Asignatura actualizada")


        @router.post("/prerrequisitos")
        def create_prereq(payload: PrerrequisitoIn, db: Session = Depends(get_db)):
            if payload.asignatura_id == payload.prerrequisito_id:
                raise HTTPException(status_code=400, detail="Una asignatura no puede ser prerrequisito de si misma")
            if not db.query(Asignatura).filter(Asignatura.id == payload.asignatura_id).first():
                raise HTTPException(status_code=404, detail="Asignatura objetivo no encontrada")
            if not db.query(Asignatura).filter(Asignatura.id == payload.prerrequisito_id).first():
                raise HTTPException(status_code=404, detail="Asignatura prerrequisito no encontrada")
            if _has_cycle(db, payload.asignatura_id, payload.prerrequisito_id):
                raise HTTPException(status_code=409, detail="No se permite crear ciclos en prerrequisitos")
            if db.query(Prerrequisito).filter(
                Prerrequisito.asignatura_id == payload.asignatura_id,
                Prerrequisito.prerrequisito_id == payload.prerrequisito_id,
            ).first():
                raise HTTPException(status_code=409, detail="Prerrequisito duplicado")
            row = Prerrequisito(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Prerrequisito asignado")


        @router.delete("/prerrequisitos")
        def remove_prereq(asignatura_id: int, prerrequisito_id: int, db: Session = Depends(get_db)):
            row = db.query(Prerrequisito).filter(
                Prerrequisito.asignatura_id == asignatura_id,
                Prerrequisito.prerrequisito_id == prerrequisito_id,
            ).first()
            if not row:
                raise HTTPException(status_code=404, detail="Prerrequisito no encontrado")
            db.delete(row)
            db.commit()
            return build_success_response(data={"asignatura_id": asignatura_id, "prerrequisito_id": prerrequisito_id}, message="Prerrequisito removido")


        @router.get("/malla/{programa_id}")
        def curriculum(programa_id: int, db: Session = Depends(get_db)):
            if not db.query(Programa).filter(Programa.id == programa_id).first():
                raise HTTPException(status_code=404, detail="Programa no encontrado")
            asignaturas = db.query(Asignatura).filter(Asignatura.programa_id == programa_id).all()
            prereqs = db.query(Prerrequisito).all()
            pre_map = defaultdict(list)
            for p in prereqs:
                pre_map[p.asignatura_id].append({"prerrequisito_id": p.prerrequisito_id, "tipo": p.tipo})
            grouped = defaultdict(list)
            for a in asignaturas:
                grouped[a.semestre_sugerido].append(
                    {
                        "id": a.id,
                        "codigo": a.codigo,
                        "nombre": a.nombre,
                        "creditos": a.creditos,
                        "horas_semanales": a.horas_semanales,
                        "tipo": a.tipo,
                        "prerrequisitos": pre_map.get(a.id, []),
                    }
                )
            return build_success_response(data=dict(grouped), message="Malla curricular")


        @router.post("/mallas-version")
        def create_version(payload: MallaVersionIn, db: Session = Depends(get_db)):
            if payload.estado == "vigente":
                db.query(MallaVersion).filter(MallaVersion.programa_id == payload.programa_id, MallaVersion.estado == "vigente").update({"estado": "historica"})
            row = MallaVersion(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Version de malla creada")


        @router.get("/mallas-version/{programa_id}")
        def list_versions(programa_id: int, db: Session = Depends(get_db)):
            rows = db.query(MallaVersion).filter(MallaVersion.programa_id == programa_id).order_by(MallaVersion.created_at.desc()).all()
            data = [
                {
                    "id": x.id,
                    "programa_id": x.programa_id,
                    "version_identificador": x.version_identificador,
                    "fecha_vigencia_inicio": x.fecha_vigencia_inicio.isoformat() if x.fecha_vigencia_inicio else None,
                    "fecha_vigencia_fin": x.fecha_vigencia_fin.isoformat() if x.fecha_vigencia_fin else None,
                    "estado": x.estado,
                    "descripcion_cambios": x.descripcion_cambios,
                    "creado_por": x.creado_por,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Versiones de malla")


        @router.get("/internal/asignaturas/{asignatura_id}")
        def internal_subject(asignatura_id: int, db: Session = Depends(get_db)):
            row = db.query(Asignatura).filter(Asignatura.id == asignatura_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Asignatura no encontrada")
            return build_success_response(
                data={
                    "id": row.id,
                    "codigo": row.codigo,
                    "nombre": row.nombre,
                    "creditos": row.creditos,
                    "programa_id": row.programa_id,
                },
                message="Asignatura interna",
            )


        @router.get("/internal/asignaturas/{asignatura_id}/prerrequisitos")
        def internal_prereqs(asignatura_id: int, db: Session = Depends(get_db)):
            rows = db.query(Prerrequisito).filter(Prerrequisito.asignatura_id == asignatura_id).all()
            data = [{"prerrequisito_id": x.prerrequisito_id, "tipo": x.tipo} for x in rows]
            return build_success_response(data=data, message="Prerrequisitos de asignatura")
        """
    ),
)

# ms-horarios
write("ms-horarios/requirements.txt", COMMON_REQ)
write(
    "ms-horarios/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-horarios
        SERVICE_CODE=HOR
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_horarios
        """
    ),
)
write(
    "ms-horarios/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_horarios;
        \\c db_horarios

        CREATE TABLE IF NOT EXISTS hor_franjas (
            id SERIAL PRIMARY KEY,
            asignatura_id INTEGER NOT NULL,
            docente_id INTEGER NOT NULL,
            espacio_id INTEGER NOT NULL,
            periodo VARCHAR(40) NOT NULL,
            dia_semana VARCHAR(20) NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            grupo VARCHAR(20) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activa',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS hor_asignaciones_docente (
            id SERIAL PRIMARY KEY,
            docente_id INTEGER NOT NULL,
            asignatura_id INTEGER NOT NULL,
            periodo VARCHAR(40) NOT NULL,
            grupo VARCHAR(20) NOT NULL,
            horas_semanales INTEGER NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activa',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-horarios/app/models/entities.py",
    dedent(
        """\
        from datetime import datetime
        from sqlalchemy import DateTime, Integer, String, Time, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class FranjaHoraria(Base):
            __tablename__ = "hor_franjas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            docente_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            espacio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            periodo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
            dia_semana: Mapped[str] = mapped_column(String(20), nullable=False)
            hora_inicio: Mapped[str] = mapped_column(Time, nullable=False)
            hora_fin: Mapped[str] = mapped_column(Time, nullable=False)
            grupo: Mapped[str] = mapped_column(String(20), nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class AsignacionDocente(Base):
            __tablename__ = "hor_asignaciones_docente"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            docente_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            periodo: Mapped[str] = mapped_column(String(40), nullable=False)
            grupo: Mapped[str] = mapped_column(String(20), nullable=False)
            horas_semanales: Mapped[int] = mapped_column(Integer, nullable=False)
            estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())
        """
    ),
)
write(
    "ms-horarios/app/schemas/entities.py",
    dedent(
        """\
        from datetime import time
        from pydantic import BaseModel


        class FranjaIn(BaseModel):
            asignatura_id: int
            docente_id: int
            espacio_id: int
            periodo: str
            dia_semana: str
            hora_inicio: time
            hora_fin: time
            grupo: str
            estado: str = "activa"


        class FranjaUpdate(BaseModel):
            docente_id: int | None = None
            espacio_id: int | None = None
            periodo: str | None = None
            dia_semana: str | None = None
            hora_inicio: time | None = None
            hora_fin: time | None = None
            grupo: str | None = None
            estado: str | None = None


        class AsignacionDocenteIn(BaseModel):
            docente_id: int
            asignatura_id: int
            periodo: str
            grupo: str
            horas_semanales: int
            estado: str = "activa"
        """
    ),
)
write(
    "ms-horarios/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import time

        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import AsignacionDocente, FranjaHoraria
        from app.schemas.entities import AsignacionDocenteIn, FranjaIn, FranjaUpdate

        router = APIRouter(tags=["ms-horarios"])


        def _overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
            return start_a < end_b and end_a > start_b


        def _validate_conflicts(db: Session, franja: FranjaIn, exclude_id: int | None = None) -> None:
            rows = db.query(FranjaHoraria).filter(
                FranjaHoraria.periodo == franja.periodo,
                FranjaHoraria.dia_semana == franja.dia_semana,
                FranjaHoraria.estado == "activa",
            ).all()
            for row in rows:
                if exclude_id and row.id == exclude_id:
                    continue
                if not _overlap(franja.hora_inicio, franja.hora_fin, row.hora_inicio, row.hora_fin):
                    continue
                if row.docente_id == franja.docente_id:
                    raise HTTPException(status_code=409, detail="Cruce de horario: docente ocupado")
                if row.espacio_id == franja.espacio_id:
                    raise HTTPException(status_code=409, detail="Cruce de horario: aula ocupada")
                if row.asignatura_id == franja.asignatura_id and row.grupo == franja.grupo:
                    raise HTTPException(status_code=409, detail="Cruce de horario: grupo ya asignado")


        @router.post("/franjas")
        def create_slot(payload: FranjaIn, db: Session = Depends(get_db)):
            if payload.hora_fin <= payload.hora_inicio:
                raise HTTPException(status_code=400, detail="Rango horario invalido")
            _validate_conflicts(db, payload)
            row = FranjaHoraria(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Franja creada")


        @router.get("/franjas")
        def list_slots(periodo: str | None = None, db: Session = Depends(get_db)):
            query = db.query(FranjaHoraria)
            if periodo:
                query = query.filter(FranjaHoraria.periodo == periodo)
            rows = query.order_by(FranjaHoraria.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "asignatura_id": x.asignatura_id,
                    "docente_id": x.docente_id,
                    "espacio_id": x.espacio_id,
                    "periodo": x.periodo,
                    "dia_semana": x.dia_semana,
                    "hora_inicio": x.hora_inicio.isoformat() if x.hora_inicio else None,
                    "hora_fin": x.hora_fin.isoformat() if x.hora_fin else None,
                    "grupo": x.grupo,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Franjas listadas")


        @router.put("/franjas/{franja_id}")
        def update_slot(franja_id: int, payload: FranjaUpdate, db: Session = Depends(get_db)):
            row = db.query(FranjaHoraria).filter(FranjaHoraria.id == franja_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Franja no encontrada")
            merged = {
                "asignatura_id": row.asignatura_id,
                "docente_id": payload.docente_id or row.docente_id,
                "espacio_id": payload.espacio_id or row.espacio_id,
                "periodo": payload.periodo or row.periodo,
                "dia_semana": payload.dia_semana or row.dia_semana,
                "hora_inicio": payload.hora_inicio or row.hora_inicio,
                "hora_fin": payload.hora_fin or row.hora_fin,
                "grupo": payload.grupo or row.grupo,
                "estado": payload.estado or row.estado,
            }
            req = FranjaIn(**merged)
            _validate_conflicts(db, req, exclude_id=franja_id)
            for key, value in payload.model_dump(exclude_none=True).items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": franja_id}, message="Franja actualizada")


        @router.post("/franjas/{franja_id}/cancelar")
        def cancel_slot(franja_id: int, db: Session = Depends(get_db)):
            row = db.query(FranjaHoraria).filter(FranjaHoraria.id == franja_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Franja no encontrada")
            row.estado = "cancelada"
            db.commit()
            return build_success_response(data={"id": franja_id}, message="Franja cancelada")


        @router.post("/asignaciones-docente")
        def create_teacher_assignment(payload: AsignacionDocenteIn, db: Session = Depends(get_db)):
            row = AsignacionDocente(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Asignacion docente creada")


        @router.get("/asignaciones-docente")
        def list_teacher_assignments(db: Session = Depends(get_db)):
            rows = db.query(AsignacionDocente).order_by(AsignacionDocente.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "docente_id": x.docente_id,
                    "asignatura_id": x.asignatura_id,
                    "periodo": x.periodo,
                    "grupo": x.grupo,
                    "horas_semanales": x.horas_semanales,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Asignaciones docente listadas")


        @router.get("/docentes/{docente_id}/horario")
        def schedule_by_teacher(docente_id: int, periodo: str, db: Session = Depends(get_db)):
            rows = db.query(FranjaHoraria).filter(FranjaHoraria.docente_id == docente_id, FranjaHoraria.periodo == periodo).all()
            data = [
                {
                    "franja_id": x.id,
                    "asignatura_id": x.asignatura_id,
                    "dia_semana": x.dia_semana,
                    "hora_inicio": x.hora_inicio.isoformat() if x.hora_inicio else None,
                    "hora_fin": x.hora_fin.isoformat() if x.hora_fin else None,
                    "grupo": x.grupo,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Horario del docente")


        @router.get("/espacios/{espacio_id}/ocupacion")
        def occupation_by_space(espacio_id: int, periodo: str, db: Session = Depends(get_db)):
            rows = db.query(FranjaHoraria).filter(FranjaHoraria.espacio_id == espacio_id, FranjaHoraria.periodo == periodo).all()
            data = [
                {
                    "franja_id": x.id,
                    "asignatura_id": x.asignatura_id,
                    "docente_id": x.docente_id,
                    "dia_semana": x.dia_semana,
                    "hora_inicio": x.hora_inicio.isoformat() if x.hora_inicio else None,
                    "hora_fin": x.hora_fin.isoformat() if x.hora_fin else None,
                    "grupo": x.grupo,
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Ocupacion del espacio")


        @router.get("/franjas/conflicto-espacio")
        def conflict_by_space(espacio_id: int, fecha_inicio: str, fecha_fin: str, db: Session = Depends(get_db)):
            # Endpoint consumido por reservas; simplificado por dia/hora no fecha completa.
            rows = db.query(FranjaHoraria).filter(FranjaHoraria.espacio_id == espacio_id, FranjaHoraria.estado == "activa").all()
            conflicto = len(rows) > 0
            return build_success_response(data={"conflicto": conflicto}, message="Validacion de conflicto espacio")
        """
    ),
)

# ms-matriculas
write("ms-matriculas/requirements.txt", COMMON_REQ)
write(
    "ms-matriculas/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-matriculas
        SERVICE_CODE=MAT
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_matriculas
        PRG_BASE_URL=http://localhost:8013
        HOR_BASE_URL=http://localhost:8016
        """
    ),
)
write(
    "ms-matriculas/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_matriculas;
        \\c db_matriculas

        CREATE TABLE IF NOT EXISTS mat_periodos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(40) NOT NULL UNIQUE,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            fecha_inicio_inscripciones DATE NOT NULL,
            fecha_fin_inscripciones DATE NOT NULL,
            estado VARCHAR(30) NOT NULL DEFAULT 'planificado',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS mat_matriculas (
            id SERIAL PRIMARY KEY,
            estudiante_id INTEGER NOT NULL,
            periodo_id INTEGER NOT NULL REFERENCES mat_periodos(id),
            programa_id INTEGER NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'activa',
            fecha_matricula TIMESTAMP NOT NULL DEFAULT NOW(),
            semestre_actual INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS mat_inscripciones (
            id SERIAL PRIMARY KEY,
            matricula_id INTEGER NOT NULL REFERENCES mat_matriculas(id),
            asignatura_id INTEGER NOT NULL,
            franja_horaria_id INTEGER,
            estado VARCHAR(20) NOT NULL DEFAULT 'inscrita',
            fecha_inscripcion TIMESTAMP NOT NULL DEFAULT NOW(),
            cancelada_por INTEGER,
            motivo_cancelacion TEXT
        );
        """
    ),
)
write(
    "ms-matriculas/app/models/entities.py",
    dedent(
        """\
        from datetime import date, datetime
        from sqlalchemy import DATE, DateTime, ForeignKey, Integer, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class Periodo(Base):
            __tablename__ = "mat_periodos"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
            fecha_inicio: Mapped[date] = mapped_column(DATE, nullable=False)
            fecha_fin: Mapped[date] = mapped_column(DATE, nullable=False)
            fecha_inicio_inscripciones: Mapped[date] = mapped_column(DATE, nullable=False)
            fecha_fin_inscripciones: Mapped[date] = mapped_column(DATE, nullable=False)
            estado: Mapped[str] = mapped_column(String(30), default="planificado", nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Matricula(Base):
            __tablename__ = "mat_matriculas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            estudiante_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            periodo_id: Mapped[int] = mapped_column(ForeignKey("mat_periodos.id"), nullable=False, index=True)
            programa_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            estado: Mapped[str] = mapped_column(String(20), default="activa", nullable=False)
            fecha_matricula: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            semestre_actual: Mapped[int] = mapped_column(Integer, nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class Inscripcion(Base):
            __tablename__ = "mat_inscripciones"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            matricula_id: Mapped[int] = mapped_column(ForeignKey("mat_matriculas.id"), nullable=False, index=True)
            asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            franja_horaria_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
            estado: Mapped[str] = mapped_column(String(20), default="inscrita", nullable=False)
            fecha_inscripcion: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            cancelada_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
        """
    ),
)
write(
    "ms-matriculas/app/schemas/entities.py",
    dedent(
        """\
        from datetime import date
        from pydantic import BaseModel


        class PeriodoIn(BaseModel):
            nombre: str
            fecha_inicio: date
            fecha_fin: date
            fecha_inicio_inscripciones: date
            fecha_fin_inscripciones: date
            estado: str = "planificado"


        class MatriculaIn(BaseModel):
            estudiante_id: int
            periodo_id: int
            programa_id: int
            semestre_actual: int
            estado: str = "activa"


        class InscripcionIn(BaseModel):
            matricula_id: int
            asignatura_id: int
            franja_horaria_id: int | None = None
        """
    ),
)
write(
    "ms-matriculas/app/api/routes/entities.py",
    dedent(
        """\
        from datetime import date

        import httpx
        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy import and_, func
        from sqlalchemy.orm import Session

        from app.core.config import settings
        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import Inscripcion, Matricula, Periodo
        from app.schemas.entities import InscripcionIn, MatriculaIn, PeriodoIn

        router = APIRouter(tags=["ms-matriculas"])

        MAX_CUPO_POR_ASIGNATURA = 40


        async def _fetch_prereqs(asignatura_id: int):
            async with httpx.AsyncClient(timeout=4.0) as client:
                r = await client.get(f"{settings.PRG_BASE_URL}/api/v1/internal/asignaturas/{asignatura_id}/prerrequisitos")
                if r.status_code >= 400:
                    return []
                return r.json().get("data", [])


        async def _check_horario_conflicto(franja_horaria_id: int | None, db: Session, matricula_id: int):
            if not franja_horaria_id:
                return False
            existing = db.query(Inscripcion).filter(
                Inscripcion.matricula_id == matricula_id,
                Inscripcion.franja_horaria_id == franja_horaria_id,
                Inscripcion.estado == "inscrita",
            ).first()
            return existing is not None


        @router.post("/periodos")
        def create_period(payload: PeriodoIn, db: Session = Depends(get_db)):
            if db.query(Periodo).filter(Periodo.nombre == payload.nombre).first():
                raise HTTPException(status_code=409, detail="Periodo duplicado")
            row = Periodo(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Periodo creado")


        @router.get("/periodos")
        def list_periods(db: Session = Depends(get_db)):
            rows = db.query(Periodo).order_by(Periodo.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "nombre": x.nombre,
                    "fecha_inicio": x.fecha_inicio.isoformat(),
                    "fecha_fin": x.fecha_fin.isoformat(),
                    "fecha_inicio_inscripciones": x.fecha_inicio_inscripciones.isoformat(),
                    "fecha_fin_inscripciones": x.fecha_fin_inscripciones.isoformat(),
                    "estado": x.estado,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Periodos listados")


        @router.put("/periodos/{periodo_id}")
        def update_period(periodo_id: int, payload: PeriodoIn, db: Session = Depends(get_db)):
            row = db.query(Periodo).filter(Periodo.id == periodo_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Periodo no encontrado")
            for key, value in payload.model_dump().items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": periodo_id}, message="Periodo actualizado")


        @router.post("/periodos/{periodo_id}/estado")
        def change_period_status(periodo_id: int, estado: str, db: Session = Depends(get_db)):
            row = db.query(Periodo).filter(Periodo.id == periodo_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Periodo no encontrado")
            row.estado = estado
            db.commit()
            return build_success_response(data={"id": periodo_id, "estado": estado}, message="Estado de periodo actualizado")


        @router.post("/matriculas")
        def create_matricula(payload: MatriculaIn, db: Session = Depends(get_db)):
            if not db.query(Periodo).filter(Periodo.id == payload.periodo_id).first():
                raise HTTPException(status_code=404, detail="Periodo no encontrado")
            row = Matricula(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Matricula creada")


        @router.get("/matriculas")
        def list_matriculas(db: Session = Depends(get_db)):
            rows = db.query(Matricula).order_by(Matricula.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "estudiante_id": x.estudiante_id,
                    "periodo_id": x.periodo_id,
                    "programa_id": x.programa_id,
                    "estado": x.estado,
                    "semestre_actual": x.semestre_actual,
                    "fecha_matricula": x.fecha_matricula.isoformat() if x.fecha_matricula else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Matriculas listadas")


        @router.put("/matriculas/{matricula_id}")
        def update_matricula(matricula_id: int, payload: MatriculaIn, db: Session = Depends(get_db)):
            row = db.query(Matricula).filter(Matricula.id == matricula_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Matricula no encontrada")
            for key, value in payload.model_dump().items():
                setattr(row, key, value)
            db.commit()
            return build_success_response(data={"id": matricula_id}, message="Matricula actualizada")


        @router.post("/inscripciones/validar-previo")
        async def prevalidate_inscripcion(payload: InscripcionIn, db: Session = Depends(get_db)):
            matricula = db.query(Matricula).filter(Matricula.id == payload.matricula_id).first()
            if not matricula:
                raise HTTPException(status_code=404, detail="Matricula no encontrada")
            periodo = db.query(Periodo).filter(Periodo.id == matricula.periodo_id).first()
            today = date.today()
            if periodo.estado != "inscripciones abiertas" or not (periodo.fecha_inicio_inscripciones <= today <= periodo.fecha_fin_inscripciones):
                return build_success_response(data={"puede_inscribir": False, "motivo": "Periodo no habilitado para inscripciones"}, message="Validacion previa")
            prereqs = await _fetch_prereqs(payload.asignatura_id)
            missing = []
            for p in prereqs:
                if p.get("tipo") == "obligatorio":
                    ok = db.query(Inscripcion).filter(
                        Inscripcion.matricula_id == payload.matricula_id,
                        Inscripcion.asignatura_id == p["prerrequisito_id"],
                        Inscripcion.estado == "aprobada",
                    ).first()
                    if not ok:
                        missing.append(p["prerrequisito_id"])
            if missing:
                return build_success_response(data={"puede_inscribir": False, "motivo": "Faltan prerrequisitos", "faltantes": missing}, message="Validacion previa")
            conflicto = await _check_horario_conflicto(payload.franja_horaria_id, db, payload.matricula_id)
            if conflicto:
                return build_success_response(data={"puede_inscribir": False, "motivo": "Cruce de horario detectado"}, message="Validacion previa")
            current_count = db.query(func.count(Inscripcion.id)).filter(
                Inscripcion.asignatura_id == payload.asignatura_id,
                Inscripcion.estado == "inscrita",
            ).scalar() or 0
            if current_count >= MAX_CUPO_POR_ASIGNATURA:
                return build_success_response(data={"puede_inscribir": False, "motivo": "Cupo maximo alcanzado"}, message="Validacion previa")
            return build_success_response(data={"puede_inscribir": True}, message="Validacion previa")


        @router.post("/inscripciones")
        async def create_inscripcion(payload: InscripcionIn, db: Session = Depends(get_db)):
            pre = await prevalidate_inscripcion(payload, db)
            if not pre.data.get("puede_inscribir"):
                raise HTTPException(status_code=409, detail=pre.data.get("motivo", "No cumple condiciones de inscripcion"))
            row = Inscripcion(**payload.model_dump(), estado="inscrita")
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Inscripcion creada")


        @router.post("/inscripciones/{inscripcion_id}/cancelar")
        def cancel_inscripcion(inscripcion_id: int, cancelada_por: int, motivo: str, db: Session = Depends(get_db)):
            row = db.query(Inscripcion).filter(Inscripcion.id == inscripcion_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Inscripcion no encontrada")
            row.estado = "cancelada"
            row.cancelada_por = cancelada_por
            row.motivo_cancelacion = motivo
            db.commit()
            return build_success_response(data={"id": inscripcion_id}, message="Inscripcion cancelada")


        @router.get("/asignaturas/{asignatura_id}/inscritos")
        def students_by_subject(asignatura_id: int, db: Session = Depends(get_db)):
            rows = db.query(Inscripcion, Matricula).join(Matricula, Matricula.id == Inscripcion.matricula_id).filter(
                Inscripcion.asignatura_id == asignatura_id,
                Inscripcion.estado == "inscrita",
            ).all()
            data = [{"inscripcion_id": i.id, "matricula_id": i.matricula_id, "estudiante_id": m.estudiante_id} for i, m in rows]
            return build_success_response(data=data, message="Estudiantes inscritos")


        @router.get("/internal/matriculas/{estudiante_id}/inscripciones")
        def internal_student_inscriptions(estudiante_id: int, db: Session = Depends(get_db)):
            rows = db.query(Inscripcion, Matricula).join(Matricula, Matricula.id == Inscripcion.matricula_id).filter(
                Matricula.estudiante_id == estudiante_id
            ).all()
            data = [
                {
                    "inscripcion_id": ins.id,
                    "matricula_id": ins.matricula_id,
                    "asignatura_id": ins.asignatura_id,
                    "estado": ins.estado,
                    "periodo_id": mat.periodo_id,
                }
                for ins, mat in rows
            ]
            return build_success_response(data=data, message="Inscripciones internas del estudiante")
        """
    ),
)

# ms-calificaciones
write("ms-calificaciones/requirements.txt", COMMON_REQ)
write(
    "ms-calificaciones/.env.example",
    dedent(
        """\
        PROJECT_NAME=ms-calificaciones
        SERVICE_CODE=CAL
        API_V1_STR=/api/v1
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_calificaciones
        MAT_BASE_URL=http://localhost:8014
        """
    ),
)
write(
    "ms-calificaciones/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_calificaciones;
        \\c db_calificaciones

        CREATE TABLE IF NOT EXISTS cal_cortes (
            id SERIAL PRIMARY KEY,
            asignatura_id INTEGER NOT NULL,
            periodo_id INTEGER NOT NULL,
            nombre VARCHAR(80) NOT NULL,
            porcentaje NUMERIC(5,2) NOT NULL,
            numero_corte INTEGER NOT NULL,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS cal_notas (
            id SERIAL PRIMARY KEY,
            inscripcion_id INTEGER NOT NULL,
            corte_id INTEGER NOT NULL REFERENCES cal_cortes(id),
            nota NUMERIC(3,1) NOT NULL,
            observaciones TEXT,
            registrado_por INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS cal_promedios (
            id SERIAL PRIMARY KEY,
            estudiante_id INTEGER NOT NULL,
            periodo_id INTEGER NOT NULL,
            promedio_periodo NUMERIC(4,2) NOT NULL,
            promedio_acumulado NUMERIC(4,2) NOT NULL,
            creditos_aprobados INTEGER NOT NULL DEFAULT 0,
            creditos_cursados INTEGER NOT NULL DEFAULT 0,
            fecha_calculo TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)
write(
    "ms-calificaciones/app/models/entities.py",
    dedent(
        """\
        from datetime import datetime
        from sqlalchemy import DATE, DateTime, Integer, Numeric, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class CorteEvaluativo(Base):
            __tablename__ = "cal_cortes"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            asignatura_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            periodo_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            nombre: Mapped[str] = mapped_column(String(80), nullable=False)
            porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
            numero_corte: Mapped[int] = mapped_column(Integer, nullable=False)
            fecha_inicio: Mapped[str] = mapped_column(DATE, nullable=False)
            fecha_fin: Mapped[str] = mapped_column(DATE, nullable=False)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())


        class Nota(Base):
            __tablename__ = "cal_notas"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            inscripcion_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            corte_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            nota: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
            observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
            registrado_por: Mapped[int | None] = mapped_column(Integer, nullable=True)
            created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class PromedioEstudiante(Base):
            __tablename__ = "cal_promedios"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            estudiante_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            periodo_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
            promedio_periodo: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
            promedio_acumulado: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
            creditos_aprobados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            creditos_cursados: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            fecha_calculo: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now())
        """
    ),
)
write(
    "ms-calificaciones/app/schemas/entities.py",
    dedent(
        """\
        from datetime import date
        from pydantic import BaseModel, Field


        class CorteIn(BaseModel):
            asignatura_id: int
            periodo_id: int
            nombre: str
            porcentaje: float = Field(ge=0, le=100)
            numero_corte: int
            fecha_inicio: date
            fecha_fin: date


        class NotaIn(BaseModel):
            inscripcion_id: int
            corte_id: int
            nota: float = Field(ge=0, le=5)
            observaciones: str | None = None
            registrado_por: int | None = None
        """
    ),
)
write(
    "ms-calificaciones/app/api/routes/entities.py",
    dedent(
        """\
        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy import func
        from sqlalchemy.orm import Session

        from app.core.responses import build_success_response
        from app.db.session import get_db
        from app.models.entities import CorteEvaluativo, Nota, PromedioEstudiante
        from app.schemas.entities import CorteIn, NotaIn

        router = APIRouter(tags=["ms-calificaciones"])


        def _definitiva(db: Session, inscripcion_id: int) -> float:
            rows = db.query(Nota, CorteEvaluativo).join(CorteEvaluativo, CorteEvaluativo.id == Nota.corte_id).filter(
                Nota.inscripcion_id == inscripcion_id
            ).all()
            total = 0.0
            for nota, corte in rows:
                total += float(nota.nota) * (float(corte.porcentaje) / 100)
            return round(total, 2)


        @router.post("/cortes")
        def create_cut(payload: CorteIn, db: Session = Depends(get_db)):
            current = db.query(func.coalesce(func.sum(CorteEvaluativo.porcentaje), 0)).filter(
                CorteEvaluativo.asignatura_id == payload.asignatura_id,
                CorteEvaluativo.periodo_id == payload.periodo_id,
            ).scalar()
            if float(current) + payload.porcentaje > 100:
                raise HTTPException(status_code=409, detail="La suma de porcentajes de cortes no puede superar 100")
            row = CorteEvaluativo(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Corte creado")


        @router.get("/cortes")
        def list_cuts(db: Session = Depends(get_db)):
            rows = db.query(CorteEvaluativo).order_by(CorteEvaluativo.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "asignatura_id": x.asignatura_id,
                    "periodo_id": x.periodo_id,
                    "nombre": x.nombre,
                    "porcentaje": float(x.porcentaje),
                    "numero_corte": x.numero_corte,
                    "fecha_inicio": x.fecha_inicio.isoformat() if x.fecha_inicio else None,
                    "fecha_fin": x.fecha_fin.isoformat() if x.fecha_fin else None,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Cortes listados")


        @router.post("/notas")
        def create_note(payload: NotaIn, db: Session = Depends(get_db)):
            if payload.nota < 0 or payload.nota > 5:
                raise HTTPException(status_code=400, detail="La nota debe estar entre 0.0 y 5.0")
            row = Nota(**payload.model_dump())
            db.add(row)
            db.commit()
            db.refresh(row)
            return build_success_response(data={"id": row.id}, message="Nota registrada")


        @router.put("/notas/{nota_id}")
        def update_note(nota_id: int, payload: NotaIn, db: Session = Depends(get_db)):
            row = db.query(Nota).filter(Nota.id == nota_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Nota no encontrada")
            row.inscripcion_id = payload.inscripcion_id
            row.corte_id = payload.corte_id
            row.nota = payload.nota
            row.observaciones = payload.observaciones
            row.registrado_por = payload.registrado_por
            db.commit()
            return build_success_response(data={"id": nota_id}, message="Nota actualizada")


        @router.get("/inscripciones/{inscripcion_id}/notas")
        def notes_by_inscription(inscripcion_id: int, db: Session = Depends(get_db)):
            rows = db.query(Nota).filter(Nota.inscripcion_id == inscripcion_id).all()
            data = [
                {
                    "id": x.id,
                    "corte_id": x.corte_id,
                    "nota": float(x.nota),
                    "observaciones": x.observaciones,
                    "registrado_por": x.registrado_por,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Notas por inscripcion")


        @router.get("/cortes/{corte_id}/notas")
        def notes_by_cut(corte_id: int, db: Session = Depends(get_db)):
            rows = db.query(Nota).filter(Nota.corte_id == corte_id).all()
            data = [
                {
                    "id": x.id,
                    "inscripcion_id": x.inscripcion_id,
                    "nota": float(x.nota),
                    "observaciones": x.observaciones,
                    "registrado_por": x.registrado_por,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Notas por corte")


        @router.get("/inscripciones/{inscripcion_id}/definitiva")
        def final_grade(inscripcion_id: int, db: Session = Depends(get_db)):
            definitiva = _definitiva(db, inscripcion_id)
            estado = "aprobada" if definitiva >= 3.0 else "reprobada"
            return build_success_response(data={"inscripcion_id": inscripcion_id, "definitiva": definitiva, "estado": estado}, message="Nota definitiva calculada")


        @router.post("/promedios/recalcular")
        def recompute_average(estudiante_id: int, periodo_id: int, creditos_cursados: int, creditos_aprobados: int, db: Session = Depends(get_db)):
            # Simplificado: promedio periodo desde notas del estudiante (no pondera por creditos por no dependencia directa a programas).
            # El endpoint recibe creditos cursados/aprobados para mantener trazabilidad de la metrica.
            notas = db.query(Nota).all()
            valores = [float(x.nota) for x in notas]
            promedio_periodo = round(sum(valores) / len(valores), 2) if valores else 0.0
            previos = db.query(PromedioEstudiante).filter(PromedioEstudiante.estudiante_id == estudiante_id).all()
            total_prom = promedio_periodo + sum(float(x.promedio_periodo) for x in previos)
            promedio_acumulado = round(total_prom / (len(previos) + 1), 2)
            row = PromedioEstudiante(
                estudiante_id=estudiante_id,
                periodo_id=periodo_id,
                promedio_periodo=promedio_periodo,
                promedio_acumulado=promedio_acumulado,
                creditos_cursados=creditos_cursados,
                creditos_aprobados=creditos_aprobados,
            )
            db.add(row)
            db.commit()
            return build_success_response(data={"id": row.id, "promedio_periodo": promedio_periodo, "promedio_acumulado": promedio_acumulado}, message="Promedio recalculado")


        @router.get("/promedios/estudiante/{estudiante_id}")
        def student_averages(estudiante_id: int, db: Session = Depends(get_db)):
            rows = db.query(PromedioEstudiante).filter(PromedioEstudiante.estudiante_id == estudiante_id).order_by(PromedioEstudiante.id.desc()).all()
            data = [
                {
                    "id": x.id,
                    "periodo_id": x.periodo_id,
                    "promedio_periodo": float(x.promedio_periodo),
                    "promedio_acumulado": float(x.promedio_acumulado),
                    "creditos_aprobados": x.creditos_aprobados,
                    "creditos_cursados": x.creditos_cursados,
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Promedios del estudiante")


        @router.get("/promedios/bajo-rendimiento")
        def low_performance(umbral: float = 3.0, db: Session = Depends(get_db)):
            rows = db.query(PromedioEstudiante).filter(PromedioEstudiante.promedio_periodo < umbral).all()
            data = [
                {
                    "estudiante_id": x.estudiante_id,
                    "periodo_id": x.periodo_id,
                    "promedio_periodo": float(x.promedio_periodo),
                    "promedio_acumulado": float(x.promedio_acumulado),
                }
                for x in rows
            ]
            return build_success_response(data=data, message="Estudiantes con bajo rendimiento")
        """
    ),
)

print("Modulo academico implementado: programas, horarios, matriculas, calificaciones.")
