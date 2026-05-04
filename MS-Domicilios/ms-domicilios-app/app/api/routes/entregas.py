from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies.security import require_permission
from app.api.schemas.response import StandardResponse
from app.core.permissions import (
    PERM_CALIFICACION_REGISTRAR,
    PERM_ENTREGA_ASIGNAR,
    PERM_ENTREGA_CONSULTAR,
    PERM_ENTREGA_CREAR,
    PERM_ENTREGA_ESTADO,
    PERM_ENTREGA_ACTUALIZAR,
    PERM_SEGUIMIENTO_CONSULTAR,
    PERM_SEGUIMIENTO_REGISTRAR,
)
from app.domain.models import (
    Calificacion,
    Entrega,
    EntregaEstado,
    Repartidor,
    RepartidorEstado,
    Seguimiento,
    SeguimientoTipo,
)
from app.infrastructure.clients.pedidos_client import pedidos_client
from app.infrastructure.database import get_db

router = APIRouter(prefix="/api/v1/entregas", tags=["entregas"])

_ALLOWED_TRANSITIONS = {
    EntregaEstado.ASIGNADA: {EntregaEstado.EN_CAMINO, EntregaEstado.FALLIDA, EntregaEstado.DEVUELTA},
    EntregaEstado.EN_CAMINO: {EntregaEstado.ENTREGADA, EntregaEstado.FALLIDA, EntregaEstado.DEVUELTA},
}


def _calcular_costo_envio(origen: str, destino: str) -> float:
    return round(5000 + (len(origen) + len(destino)) * 8.5, 2)


def _entrega_to_dict(entrega: Entrega) -> dict:
    return {
        "id": entrega.id,
        "pedido_id": entrega.pedido_id,
        "repartidor_id": entrega.repartidor_id,
        "origen": entrega.origen,
        "destino": entrega.destino,
        "observaciones": entrega.observaciones,
        "estado": entrega.estado.value,
        "costo_envio": entrega.costo_envio,
        "fecha_creacion": entrega.fecha_creacion,
        "fecha_actualizacion": entrega.fecha_actualizacion,
    }


def _seguimiento_to_dict(item: Seguimiento) -> dict:
    return {
        "id": item.id,
        "entrega_id": item.entrega_id,
        "tipo": item.tipo.value,
        "latitud": float(item.latitud),
        "longitud": float(item.longitud),
        "descripcion": item.descripcion,
        "fecha_registro": item.fecha_registro,
    }


def _calificacion_to_dict(item: Calificacion) -> dict:
    return {
        "id": item.id,
        "entrega_id": item.entrega_id,
        "repartidor_id": item.repartidor_id,
        "solicitante_id": item.solicitante_id,
        "puntaje": item.puntaje,
        "comentario": item.comentario,
        "fecha_registro": item.fecha_registro,
    }


@router.post("", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def crear_entrega(
    payload: dict,
    request: Request,
    _: dict = Depends(require_permission(PERM_ENTREGA_CREAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    required_fields = ["pedido_id", "origen", "destino"]
    missing = [field for field in required_fields if payload.get(field) in (None, "")]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "El payload contiene campos obligatorios faltantes o invalidos.",
                "data": {"campos_fallidos": missing},
            },
        )

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    pedido_lookup = await pedidos_client.lookup_pedido(int(payload["pedido_id"]), request_id=request_id)
    if not pedido_lookup.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=pedido_lookup.message or "Pedido no encontrado en ms-pedidos",
        )
    if not pedido_lookup.is_eligible:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=pedido_lookup.message or "Pedido no elegible para crear entrega",
        )

    existing = db.query(Entrega).filter(Entrega.pedido_id == int(payload["pedido_id"])).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una entrega para el pedido")

    entrega = Entrega(
        pedido_id=int(payload["pedido_id"]),
        origen=str(payload["origen"]),
        destino=str(payload["destino"]),
        observaciones=payload.get("observaciones"),
        estado=EntregaEstado.ASIGNADA,
        repartidor_id=None,
        costo_envio=_calcular_costo_envio(str(payload["origen"]), str(payload["destino"])),
    )

    db.add(entrega)
    db.commit()
    db.refresh(entrega)

    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_entrega_to_dict(entrega),
        message="Entrega creada exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/{entrega_id}", response_model=StandardResponse)
async def consultar_entrega(
    entrega_id: int,
    request: Request,
    _: dict = Depends(require_permission(PERM_ENTREGA_CONSULTAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    entrega = db.get(Entrega, entrega_id)
    if not entrega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_entrega_to_dict(entrega),
        message="Consulta de entrega exitosa.",
        timestamp=datetime.now(timezone.utc),
    )


@router.put("/{entrega_id}", response_model=StandardResponse)
async def actualizar_entrega(
    entrega_id: int,
    payload: dict,
    request: Request,
    _: dict = Depends(require_permission(PERM_ENTREGA_ACTUALIZAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    entrega = db.get(Entrega, entrega_id)
    if not entrega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    editable_fields = {"origen", "destino", "observaciones"}
    for field in editable_fields:
        if field in payload and payload[field] not in (None, ""):
            setattr(entrega, field, payload[field])

    entrega.fecha_actualizacion = datetime.now(timezone.utc)
    db.add(entrega)
    db.commit()
    db.refresh(entrega)

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_entrega_to_dict(entrega),
        message="Entrega actualizada exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/{entrega_id}/asignar", response_model=StandardResponse)
async def asignar_repartidor(
    entrega_id: int,
    payload: dict,
    request: Request,
    _: dict = Depends(require_permission(PERM_ENTREGA_ASIGNAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    repartidor_id = payload.get("repartidor_id")
    if not repartidor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="repartidor_id es obligatorio")

    entrega = db.get(Entrega, entrega_id)
    if not entrega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    if entrega.estado != EntregaEstado.ASIGNADA or entrega.repartidor_id is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La entrega no permite asignacion en su estado actual",
        )

    repartidor = db.get(Repartidor, int(repartidor_id))
    if not repartidor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repartidor no encontrado")

    if repartidor.estado != RepartidorEstado.DISPONIBLE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Repartidor no disponible")

    if repartidor.zona_cobertura.lower() not in entrega.destino.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La zona de cobertura del repartidor no coincide con el destino",
        )

    entrega.repartidor_id = repartidor.id
    entrega.fecha_actualizacion = datetime.now(timezone.utc)
    repartidor.estado = RepartidorEstado.EN_RUTA
    repartidor.fecha_actualizacion = datetime.now(timezone.utc)

    db.add(entrega)
    db.add(repartidor)
    db.commit()
    db.refresh(entrega)

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_entrega_to_dict(entrega),
        message="Repartidor asignado exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )


@router.patch("/{entrega_id}/estado", response_model=StandardResponse)
async def actualizar_estado_entrega(
    entrega_id: int,
    payload: dict,
    request: Request,
    _: dict = Depends(require_permission(PERM_ENTREGA_ESTADO)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    nuevo_estado_raw = payload.get("estado")
    if not nuevo_estado_raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="estado es obligatorio")

    try:
        nuevo_estado = EntregaEstado(nuevo_estado_raw)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado de entrega invalido") from exc

    entrega = db.get(Entrega, entrega_id)
    if not entrega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    if entrega.repartidor_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se puede actualizar el estado de una entrega sin repartidor asignado",
        )

    allowed_next = _ALLOWED_TRANSITIONS.get(entrega.estado, set())
    if nuevo_estado not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Transicion invalida: {entrega.estado.value} -> {nuevo_estado.value}",
        )

    entrega.estado = nuevo_estado
    entrega.fecha_actualizacion = datetime.now(timezone.utc)

    tracking_point = Seguimiento(
        entrega_id=entrega.id,
        tipo=SeguimientoTipo.AUTOMATICO,
        latitud=float(payload.get("latitud", 0.0)),
        longitud=float(payload.get("longitud", 0.0)),
        descripcion=payload.get("descripcion") or f"Cambio de estado a {nuevo_estado.value}",
    )
    db.add(tracking_point)

    if nuevo_estado in {EntregaEstado.ENTREGADA, EntregaEstado.FALLIDA, EntregaEstado.DEVUELTA} and entrega.repartidor_id:
        repartidor = db.get(Repartidor, entrega.repartidor_id)
        if repartidor:
            repartidor.estado = RepartidorEstado.DISPONIBLE
            repartidor.fecha_actualizacion = datetime.now(timezone.utc)
            db.add(repartidor)

    db.add(entrega)
    db.commit()
    db.refresh(entrega)

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_entrega_to_dict(entrega),
        message="Estado de entrega actualizado exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/{entrega_id}/seguimiento", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def registrar_seguimiento_manual(
    entrega_id: int,
    payload: dict,
    request: Request,
    _: dict = Depends(require_permission(PERM_SEGUIMIENTO_REGISTRAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    required_fields = ["latitud", "longitud"]
    missing = [field for field in required_fields if payload.get(field) in (None, "")]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Coordenadas invalidas", "data": {"campos_fallidos": missing}},
        )

    entrega = db.get(Entrega, entrega_id)
    if not entrega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    if entrega.estado != EntregaEstado.EN_CAMINO:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo se pueden registrar puntos manuales para entregas en camino",
        )

    lat = float(payload["latitud"])
    lon = float(payload["longitud"])
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coordenadas fuera de rango")

    seguimiento = Seguimiento(
        entrega_id=entrega.id,
        tipo=SeguimientoTipo.MANUAL,
        latitud=lat,
        longitud=lon,
        descripcion=payload.get("descripcion"),
    )

    db.add(seguimiento)
    db.commit()
    db.refresh(seguimiento)

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_seguimiento_to_dict(seguimiento),
        message="Punto de seguimiento registrado exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/{entrega_id}/seguimiento", response_model=StandardResponse)
async def consultar_historial_seguimiento(
    entrega_id: int,
    request: Request,
    _: dict = Depends(require_permission(PERM_SEGUIMIENTO_CONSULTAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    entrega = db.get(Entrega, entrega_id)
    if not entrega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    puntos = (
        db.query(Seguimiento)
        .filter(Seguimiento.entrega_id == entrega_id)
        .order_by(Seguimiento.fecha_registro.asc())
        .all()
    )

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=[_seguimiento_to_dict(item) for item in puntos],
        message="Historial de seguimiento consultado exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/{entrega_id}/calificaciones", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def registrar_calificacion(
    entrega_id: int,
    payload: dict,
    request: Request,
    auth_data: dict = Depends(require_permission(PERM_CALIFICACION_REGISTRAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    puntaje = payload.get("puntaje")
    if puntaje is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="puntaje es obligatorio")

    puntaje_int = int(puntaje)
    if puntaje_int < 1 or puntaje_int > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="puntaje debe estar entre 1 y 5")

    entrega = db.get(Entrega, entrega_id)
    if not entrega:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    if entrega.estado != EntregaEstado.ENTREGADA:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo se pueden calificar entregas en estado entregada",
        )

    existing = db.query(Calificacion).filter(Calificacion.entrega_id == entrega_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La entrega ya fue calificada")

    if not entrega.repartidor_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La entrega no tiene repartidor asociado")

    calificacion = Calificacion(
        entrega_id=entrega.id,
        repartidor_id=entrega.repartidor_id,
        solicitante_id=int(auth_data["user_id"]),
        puntaje=puntaje_int,
        comentario=payload.get("comentario"),
    )

    db.add(calificacion)
    db.flush()

    promedio = db.query(func.avg(Calificacion.puntaje)).filter(Calificacion.repartidor_id == entrega.repartidor_id).scalar()
    repartidor = db.get(Repartidor, entrega.repartidor_id)
    if repartidor:
        repartidor.calificacion_promedio = float(promedio or 0.0)
        repartidor.fecha_actualizacion = datetime.now(timezone.utc)
        db.add(repartidor)

    db.commit()
    db.refresh(calificacion)

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_calificacion_to_dict(calificacion),
        message="Calificacion registrada exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )
