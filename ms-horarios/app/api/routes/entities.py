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
