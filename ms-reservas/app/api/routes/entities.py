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
