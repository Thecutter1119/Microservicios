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
