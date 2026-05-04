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
