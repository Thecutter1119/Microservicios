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
