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
