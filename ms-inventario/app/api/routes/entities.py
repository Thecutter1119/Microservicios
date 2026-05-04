from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.middleware import get_current_request_id
from app.core.responses import build_success_response
from app.db.session import get_db
from app.models.entities import Activo, Categoria, MovimientoStock
from app.schemas.entities import ActivoIn, ActivoOut, ActivoUpdate, CategoriaIn, CategoriaOut, MovimientoIn

router = APIRouter(tags=["ms-inventario"])


def _depreciacion_linea_recta(precio: float, vida_meses: int, fecha_adq: date) -> float:
    if vida_meses <= 0:
        return 0.0
    today = date.today()
    months = (today.year - fecha_adq.year) * 12 + (today.month - fecha_adq.month)
    months = max(0, months)
    value = (precio / vida_meses) * months
    return round(min(value, precio), 2)


@router.post("/categorias")
def create_category(payload: CategoriaIn, db: Session = Depends(get_db)):
    if db.query(Categoria).filter(Categoria.nombre == payload.nombre).first():
        raise HTTPException(status_code=409, detail="La categoria ya existe")
    if payload.categoria_padre_id and not db.query(Categoria).filter(Categoria.id == payload.categoria_padre_id).first():
        raise HTTPException(status_code=404, detail="Categoria padre no encontrada")
    row = Categoria(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data=CategoriaOut.model_validate(row).model_dump(mode="json"), message="Categoria creada")


@router.get("/categorias")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Categoria).order_by(Categoria.nombre.asc()).all()
    data = [CategoriaOut.model_validate(x).model_dump(mode="json") for x in rows]
    return build_success_response(data=data, message="Categorias listadas")


@router.put("/categorias/{categoria_id}")
def update_category(categoria_id: int, payload: CategoriaIn, db: Session = Depends(get_db)):
    row = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return build_success_response(data=CategoriaOut.model_validate(row).model_dump(mode="json"), message="Categoria actualizada")


@router.post("/activos")
def create_asset(payload: ActivoIn, db: Session = Depends(get_db)):
    if db.query(Activo).filter(Activo.codigo_interno == payload.codigo_interno).first():
        raise HTTPException(status_code=409, detail="Codigo interno duplicado")
    if not db.query(Categoria).filter(Categoria.id == payload.categoria_id).first():
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    dep = _depreciacion_linea_recta(payload.precio_adquisicion, payload.vida_util_meses, payload.fecha_adquisicion)
    row = Activo(**payload.model_dump(), valor_depreciacion_actual=dep)
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data=ActivoOut.model_validate(row).model_dump(mode="json"), message="Activo creado")


@router.get("/activos")
def list_assets(db: Session = Depends(get_db)):
    rows = db.query(Activo).order_by(Activo.id.desc()).all()
    data = [ActivoOut.model_validate(x).model_dump(mode="json") for x in rows]
    return build_success_response(data=data, message="Activos listados")


@router.get("/activos/{activo_id}")
def get_asset(activo_id: int, db: Session = Depends(get_db)):
    row = db.query(Activo).filter(Activo.id == activo_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    row.valor_depreciacion_actual = _depreciacion_linea_recta(float(row.precio_adquisicion), row.vida_util_meses, row.fecha_adquisicion)
    db.commit()
    db.refresh(row)
    return build_success_response(data=ActivoOut.model_validate(row).model_dump(mode="json"), message="Activo consultado")


@router.put("/activos/{activo_id}")
def update_asset(activo_id: int, payload: ActivoUpdate, db: Session = Depends(get_db)):
    row = db.query(Activo).filter(Activo.id == activo_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(row, key, value)
    row.valor_depreciacion_actual = _depreciacion_linea_recta(float(row.precio_adquisicion), row.vida_util_meses, row.fecha_adquisicion)
    db.commit()
    db.refresh(row)
    return build_success_response(data=ActivoOut.model_validate(row).model_dump(mode="json"), message="Activo actualizado")


@router.post("/activos/{activo_id}/baja")
def soft_delete_asset(activo_id: int, db: Session = Depends(get_db)):
    row = db.query(Activo).filter(Activo.id == activo_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    row.estado = "dado de baja"
    db.commit()
    return build_success_response(data={"activo_id": activo_id}, message="Activo dado de baja")


@router.post("/movimientos")
def register_movement(payload: MovimientoIn, db: Session = Depends(get_db)):
    row = db.query(Activo).filter(Activo.id == payload.activo_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    if payload.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad debe ser mayor a cero")
    tipo = payload.tipo_movimiento.lower()
    if tipo not in {"entrada", "salida", "ajuste", "transferencia"}:
        raise HTTPException(status_code=400, detail="Tipo de movimiento invalido")
    if tipo == "salida" and row.stock_actual - payload.cantidad < 0:
        raise HTTPException(status_code=409, detail="No se permite stock negativo")
    if tipo == "entrada":
        row.stock_actual += payload.cantidad
    elif tipo == "salida":
        row.stock_actual -= payload.cantidad
    elif tipo in {"ajuste", "transferencia"}:
        row.stock_actual += payload.cantidad

    move = MovimientoStock(
        **payload.model_dump(),
        tipo_movimiento=tipo,
        request_id=get_current_request_id(),
    )
    db.add(move)
    db.commit()
    db.refresh(move)
    return build_success_response(
        data={"movimiento_id": move.id, "activo_id": row.id, "stock_actual": row.stock_actual},
        message="Movimiento registrado",
    )


@router.get("/activos/{activo_id}/movimientos")
def movement_history(activo_id: int, db: Session = Depends(get_db)):
    if not db.query(Activo).filter(Activo.id == activo_id).first():
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    rows = db.query(MovimientoStock).filter(MovimientoStock.activo_id == activo_id).order_by(MovimientoStock.created_at.desc()).all()
    data = [
        {
            "id": x.id,
            "tipo_movimiento": x.tipo_movimiento,
            "cantidad": x.cantidad,
            "motivo": x.motivo,
            "usuario_responsable_id": x.usuario_responsable_id,
            "pedido_referencia": x.pedido_referencia,
            "request_id": x.request_id,
            "created_at": x.created_at.isoformat() if x.created_at else None,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Movimientos del activo")


@router.get("/activos/stock/bajo")
def low_stock_assets(db: Session = Depends(get_db)):
    rows = db.query(Activo).filter(Activo.stock_actual <= Activo.stock_minimo).order_by(Activo.stock_actual.asc()).all()
    data = [ActivoOut.model_validate(x).model_dump(mode="json") for x in rows]
    return build_success_response(data=data, message="Activos con stock bajo")


@router.get("/depreciacion/{activo_id}")
def calculate_depreciation(activo_id: int, db: Session = Depends(get_db)):
    row = db.query(Activo).filter(Activo.id == activo_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    depreciacion = _depreciacion_linea_recta(float(row.precio_adquisicion), row.vida_util_meses, row.fecha_adquisicion)
    return build_success_response(
        data={
            "activo_id": row.id,
            "precio_adquisicion": float(row.precio_adquisicion),
            "vida_util_meses": row.vida_util_meses,
            "depreciacion_actual": depreciacion,
        },
        message="Depreciacion calculada",
    )
