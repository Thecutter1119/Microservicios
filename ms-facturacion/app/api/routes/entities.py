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
