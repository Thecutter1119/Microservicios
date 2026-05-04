from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.security import require_permission
from app.api.schemas.response import StandardResponse
from app.core.permissions import (
    PERM_REPARTIDOR_ACTUALIZAR,
    PERM_REPARTIDOR_CONSULTAR,
    PERM_REPARTIDOR_CREAR,
)
from app.domain.models import Repartidor, RepartidorEstado
from app.infrastructure.database import get_db

router = APIRouter(prefix="/api/v1/repartidores", tags=["repartidores"])


def _repartidor_to_dict(repartidor: Repartidor) -> dict:
    return {
        "id": repartidor.id,
        "usuario_id": repartidor.usuario_id,
        "nombre": repartidor.nombre,
        "telefono": repartidor.telefono,
        "tipo_vehiculo": repartidor.tipo_vehiculo,
        "placa_vehiculo": repartidor.placa_vehiculo,
        "zona_cobertura": repartidor.zona_cobertura,
        "estado": repartidor.estado.value,
        "calificacion_promedio": repartidor.calificacion_promedio,
        "fecha_registro": repartidor.fecha_registro,
        "fecha_actualizacion": repartidor.fecha_actualizacion,
    }


@router.post("", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def crear_repartidor(
    payload: dict,
    request: Request,
    _: dict = Depends(require_permission(PERM_REPARTIDOR_CREAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    required_fields = [
        "usuario_id",
        "nombre",
        "telefono",
        "tipo_vehiculo",
        "placa_vehiculo",
        "zona_cobertura",
    ]
    missing = [field for field in required_fields if payload.get(field) in (None, "")]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "El payload contiene campos obligatorios faltantes o invalidos.",
                "data": {"campos_fallidos": missing},
            },
        )

    duplicate = db.query(Repartidor).filter(Repartidor.placa_vehiculo == payload["placa_vehiculo"]).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un repartidor registrado con la placa '{payload['placa_vehiculo']}'.",
        )

    repartidor = Repartidor(
        usuario_id=int(payload["usuario_id"]),
        nombre=str(payload["nombre"]),
        telefono=str(payload["telefono"]),
        tipo_vehiculo=str(payload["tipo_vehiculo"]),
        placa_vehiculo=str(payload["placa_vehiculo"]),
        zona_cobertura=str(payload["zona_cobertura"]),
        estado=RepartidorEstado.DISPONIBLE,
        calificacion_promedio=None,
    )

    db.add(repartidor)
    db.commit()
    db.refresh(repartidor)

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_repartidor_to_dict(repartidor),
        message="Repartidor creado exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )


@router.get("", response_model=StandardResponse)
async def listar_repartidores_por_zona(
    request: Request,
    zona_cobertura: str = Query(..., min_length=1),
    _: dict = Depends(require_permission(PERM_REPARTIDOR_CONSULTAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    repartidores = (
        db.query(Repartidor)
        .filter(
            Repartidor.estado == RepartidorEstado.DISPONIBLE,
            Repartidor.zona_cobertura.ilike(zona_cobertura),
        )
        .all()
    )

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=[_repartidor_to_dict(item) for item in repartidores],
        message=(
            f"Se encontraron {len(repartidores)} repartidores disponibles en la zona '{zona_cobertura}'."
            if repartidores
            else f"No se encontraron repartidores disponibles en la zona '{zona_cobertura}'."
        ),
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/{repartidor_id}", response_model=StandardResponse)
async def consultar_repartidor_por_id(
    repartidor_id: int,
    request: Request,
    _: dict = Depends(require_permission(PERM_REPARTIDOR_CONSULTAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    repartidor = db.get(Repartidor, repartidor_id)
    if not repartidor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repartidor no encontrado")

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_repartidor_to_dict(repartidor),
        message="Consulta de repartidor exitosa.",
        timestamp=datetime.now(timezone.utc),
    )


@router.put("/{repartidor_id}", response_model=StandardResponse)
async def actualizar_repartidor(
    repartidor_id: int,
    payload: dict,
    request: Request,
    _: dict = Depends(require_permission(PERM_REPARTIDOR_ACTUALIZAR)),
    db: Session = Depends(get_db),
) -> StandardResponse:
    repartidor = db.get(Repartidor, repartidor_id)
    if not repartidor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repartidor no encontrado")

    nueva_placa = payload.get("placa_vehiculo")
    if nueva_placa and nueva_placa != repartidor.placa_vehiculo:
        duplicate = db.query(Repartidor).filter(Repartidor.placa_vehiculo == nueva_placa).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un repartidor registrado con la placa '{nueva_placa}'.",
            )

    editable_fields = ["telefono", "tipo_vehiculo", "placa_vehiculo", "zona_cobertura", "nombre"]
    for field in editable_fields:
        if field in payload and payload[field] not in (None, ""):
            setattr(repartidor, field, payload[field])

    repartidor.fecha_actualizacion = datetime.now(timezone.utc)
    db.add(repartidor)
    db.commit()
    db.refresh(repartidor)

    request_id = getattr(request.state, "request_id", "DOM-unknown")
    return StandardResponse(
        request_id=request_id,
        success=True,
        data=_repartidor_to_dict(repartidor),
        message="Repartidor actualizado exitosamente.",
        timestamp=datetime.now(timezone.utc),
    )
