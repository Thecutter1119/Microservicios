from decimal import Decimal
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.pedidos import Pedido, ItemPedido, HistorialEstado
from app.schemas.pedidos import (
    PedidoCreate, PedidoUpdate, PedidoAvanzarEstado, PedidoCancelar, 
    RegistroRecepcion, PedidoResponse, PedidoDetalleResponse, 
    ItemPedidoCreate, ItemPedidoUpdate, ItemPedidoResponse, HistorialEstadoResponse
)
from app.core.dependencies import verify_user_session_and_permission, verify_app_token
from app.core.responses import StandardResponse, build_success_response, add_audit_task
from app.clients.http_clients import ProveedorClient, InventarioClient

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

FLUJO_ESTADOS = {
    "borrador": "enviado",
    "enviado": "aprobado",
    "aprobado": "en_proceso",
    "en_proceso": "recibido"
}

ESTADOS_CANCELABLES = ["borrador", "enviado", "aprobado", "en_proceso"]

def recalcular_monto_total(db: Session, pedido: Pedido):
    total = sum(item.subtotal for item in pedido.items)
    pedido.monto_total = total
    db.commit()

@router.post("", response_model=StandardResponse[PedidoResponse], status_code=201)
async def crear_pedido(
    payload: PedidoCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_CREAR_PEDIDO")
    await ProveedorClient.validar_contrato_vigente(payload.proveedor_id)
    
    import secrets
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    numero_pedido = f"PED-{today}-{secrets.token_hex(2).upper()}"
    
    nuevo_pedido = Pedido(
        numero_pedido=numero_pedido,
        solicitante_id=user_data["usuario_id"],
        proveedor_id=payload.proveedor_id,
        estado="borrador",
        observaciones=payload.observaciones,
        monto_total=0.0
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    
    historial = HistorialEstado(
        pedido_id=nuevo_pedido.id,
        estado_nuevo="borrador",
        usuario_id=user_data["usuario_id"],
        comentario="Creación inicial del pedido"
    )
    db.add(historial)
    db.commit()
    
    add_audit_task(background_tasks, "Crear Pedido", "POST", 201, 100, user_data["usuario_id"], f"Pedido {numero_pedido} creado")
    return build_success_response(data=PedidoResponse.model_validate(nuevo_pedido), message="Pedido creado exitosamente")

@router.get("", response_model=StandardResponse[list[PedidoResponse]])
async def listar_pedidos(
    request: Request,
    background_tasks: BackgroundTasks,
    numero_pedido: str = None,
    estado: str = None,
    proveedor_id: int = None,
    solicitante_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_LISTAR_PEDIDOS")
    query = db.query(Pedido)
    
    if numero_pedido:
        query = query.filter(Pedido.numero_pedido == numero_pedido)
    else:
        if estado: query = query.filter(Pedido.estado == estado)
        if proveedor_id: query = query.filter(Pedido.proveedor_id == proveedor_id)
        if solicitante_id: query = query.filter(Pedido.solicitante_id == solicitante_id)
        
    pedidos = query.order_by(Pedido.id.desc()).offset(skip).limit(limit).all()
    
    add_audit_task(background_tasks, "Listar Pedidos", "GET", 200, 50, user_data["usuario_id"])
    return build_success_response(
        data=[PedidoResponse.model_validate(p) for p in pedidos],
        message="Listado de pedidos"
    )

@router.get("/{pedido_id}", response_model=StandardResponse[PedidoDetalleResponse])
async def consultar_pedido_por_id(
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    usuario_id = None
    if request.headers.get("Authorization"):
        user_data = await verify_user_session_and_permission(request, "PED_CONSULTAR_PEDIDO")
        usuario_id = user_data.get("usuario_id")
    else:
        await verify_app_token(request)

    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    add_audit_task(background_tasks, "Consultar Pedido", "GET", 200, 30, usuario_id)
    return build_success_response(data=PedidoDetalleResponse.model_validate(pedido), message="Detalle del pedido")

@router.put("/{pedido_id}", response_model=StandardResponse[PedidoResponse])
async def actualizar_pedido(
    payload: PedidoUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_ACTUALIZAR_PEDIDO")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    if pedido.estado != "borrador":
        raise HTTPException(status_code=400, detail="Solo se pueden modificar pedidos en estado borrador")
        
    if payload.proveedor_id is not None and payload.proveedor_id != pedido.proveedor_id:
        await ProveedorClient.validar_contrato_vigente(payload.proveedor_id)
        pedido.proveedor_id = payload.proveedor_id
        
    if payload.observaciones is not None:
        pedido.observaciones = payload.observaciones
        
    db.commit()
    db.refresh(pedido)
    
    add_audit_task(background_tasks, "Actualizar Pedido", "PUT", 200, 80, user_data["usuario_id"])
    return build_success_response(data=PedidoResponse.model_validate(pedido), message="Pedido actualizado")

@router.post("/{pedido_id}/avanzar-estado", response_model=StandardResponse[PedidoResponse])
async def avanzar_estado_pedido(
    payload: PedidoAvanzarEstado,
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_AVANZAR_ESTADO")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    estado_actual = pedido.estado
    
    if estado_actual not in FLUJO_ESTADOS:
        raise HTTPException(status_code=400, detail=f"No se puede avanzar manualmente desde el estado '{estado_actual}'")
        
    estado_nuevo = FLUJO_ESTADOS[estado_actual]
    
    if estado_actual == "borrador":
        if not pedido.items:
            raise HTTPException(status_code=400, detail="No se puede enviar un pedido sin ítems")
        await ProveedorClient.validar_contrato_vigente(pedido.proveedor_id)
    
    if estado_nuevo == "aprobado":
        pedido.fecha_aprobacion = datetime.now(timezone.utc)
        
    pedido.estado = estado_nuevo
    db.commit()
    
    historial = HistorialEstado(
        pedido_id=pedido.id,
        estado_anterior=estado_actual,
        estado_nuevo=estado_nuevo,
        usuario_id=user_data["usuario_id"],
        comentario=payload.comentario
    )
    db.add(historial)
    db.commit()
    db.refresh(pedido)
    
    add_audit_task(background_tasks, "Avanzar Estado", "POST", 200, 100, user_data["usuario_id"], f"De {estado_actual} a {estado_nuevo}")
    return build_success_response(data=PedidoResponse.model_validate(pedido), message=f"Estado avanzado a {estado_nuevo}")

@router.post("/{pedido_id}/cancelar", response_model=StandardResponse[PedidoResponse])
async def cancelar_pedido(
    payload: PedidoCancelar,
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_CANCELAR_PEDIDO")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    if pedido.estado not in ESTADOS_CANCELABLES:
        raise HTTPException(status_code=400, detail=f"No se puede cancelar un pedido en estado '{pedido.estado}'")
        
    estado_anterior = pedido.estado
    pedido.estado = "cancelado"
    db.commit()
    
    historial = HistorialEstado(
        pedido_id=pedido.id,
        estado_anterior=estado_anterior,
        estado_nuevo="cancelado",
        usuario_id=user_data["usuario_id"],
        comentario=payload.motivo
    )
    db.add(historial)
    db.commit()
    db.refresh(pedido)
    
    add_audit_task(background_tasks, "Cancelar Pedido", "POST", 200, 80, user_data["usuario_id"], f"Cancelado desde {estado_anterior}")
    return build_success_response(data=PedidoResponse.model_validate(pedido), message="Pedido cancelado")

@router.post("/{pedido_id}/items", response_model=StandardResponse[ItemPedidoResponse], status_code=201)
async def agregar_item(
    payload: ItemPedidoCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_GESTIONAR_ITEMS")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido: raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != "borrador": raise HTTPException(status_code=400, detail="Solo se pueden agregar ítems en estado borrador")
    
    await InventarioClient.verificar_existencia(payload.activo_id)
    
    cantidad_solicitada = Decimal(str(payload.cantidad_solicitada))
    valor_unitario = Decimal(str(payload.valor_unitario))
    subtotal = cantidad_solicitada * valor_unitario
    
    nuevo_item = ItemPedido(
        pedido_id=pedido.id,
        activo_id=payload.activo_id,
        descripcion=payload.descripcion,
        cantidad_solicitada=cantidad_solicitada,
        valor_unitario=valor_unitario,
        subtotal=subtotal
    )
    db.add(nuevo_item)
    db.commit()
    db.refresh(nuevo_item)
    
    recalcular_monto_total(db, pedido)
    
    add_audit_task(background_tasks, "Agregar Item", "POST", 201, 80, user_data["usuario_id"])
    return build_success_response(data=ItemPedidoResponse.model_validate(nuevo_item), message="Ítem agregado")

@router.get("/{pedido_id}/items", response_model=StandardResponse[list[ItemPedidoResponse]])
async def listar_items(
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_LISTAR_ITEMS")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    items = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido_id).all()
    add_audit_task(background_tasks, "Listar Items", "GET", 200, 20, user_data["usuario_id"])
    return build_success_response(data=[ItemPedidoResponse.model_validate(i) for i in items], message="Ítems del pedido")

@router.put("/{pedido_id}/items/{item_id}", response_model=StandardResponse[ItemPedidoResponse])
async def actualizar_item(
    payload: ItemPedidoUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_GESTIONAR_ITEMS")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != "borrador":
        raise HTTPException(status_code=400, detail="Solo se pueden actualizar ítems en estado borrador")

    item = db.query(ItemPedido).filter(ItemPedido.id == item_id, ItemPedido.pedido_id == pedido_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en este pedido")

    if payload.descripcion is not None:
        item.descripcion = payload.descripcion

    if payload.cantidad_solicitada is not None:
        item.cantidad_solicitada = Decimal(str(payload.cantidad_solicitada))

    if payload.valor_unitario is not None:
        item.valor_unitario = Decimal(str(payload.valor_unitario))

    item.subtotal = Decimal(str(item.cantidad_solicitada)) * Decimal(str(item.valor_unitario))
    db.commit()
    db.refresh(item)

    recalcular_monto_total(db, pedido)

    add_audit_task(background_tasks, "Actualizar Item", "PUT", 200, 60, user_data["usuario_id"])
    return build_success_response(data=ItemPedidoResponse.model_validate(item), message="Ítem actualizado")

@router.delete("/{pedido_id}/items/{item_id}", response_model=StandardResponse[dict])
async def remover_item(
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_GESTIONAR_ITEMS")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido: raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != "borrador": raise HTTPException(status_code=400, detail="Solo se pueden remover ítems en estado borrador")
    
    item = db.query(ItemPedido).filter(ItemPedido.id == item_id, ItemPedido.pedido_id == pedido_id).first()
    if not item: raise HTTPException(status_code=404, detail="Ítem no encontrado en este pedido")
    
    db.delete(item)
    db.commit()
    
    recalcular_monto_total(db, pedido)
    
    add_audit_task(background_tasks, "Remover Item", "DELETE", 200, 50, user_data["usuario_id"])
    return build_success_response(data={"item_id": item_id}, message="Ítem eliminado y monto recalculado")

@router.post("/{pedido_id}/recepciones", response_model=StandardResponse[PedidoResponse])
async def registrar_recepcion(
    payload: RegistroRecepcion,
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_RECEPCIONAR_PEDIDO")
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido: raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if pedido.estado not in ["en_proceso", "recibido_parcial"]:
        raise HTTPException(status_code=400, detail="El pedido no está habilitado para recibir bienes")
        
    estado_anterior_pedido = pedido.estado
    
    items_map = {i.id: i for i in pedido.items}
    
    for req_item in payload.items:
        db_item = items_map.get(req_item.item_id)
        if not db_item:
            raise HTTPException(status_code=400, detail=f"Ítem {req_item.item_id} no pertenece al pedido")
            
        pendiente = db_item.cantidad_solicitada - db_item.cantidad_recibida
        recibido = Decimal(str(req_item.cantidad_recibida))
        if recibido > pendiente:
            raise HTTPException(status_code=400, detail=f"La cantidad a recibir ({req_item.cantidad_recibida}) supera lo pendiente ({pendiente}) para el ítem {req_item.item_id}")
            
        await InventarioClient.registrar_entrada(db_item.activo_id, float(recibido), payload.observaciones or "")
        
        db_item.cantidad_recibida += recibido
        if db_item.cantidad_recibida == db_item.cantidad_solicitada:
            db_item.estado = "recibido"
        elif db_item.cantidad_recibida > 0:
            db_item.estado = "recibido_parcial"
            
    todos_recibidos = all(i.estado == "recibido" for i in pedido.items)
    
    estado_nuevo_pedido = "recibido" if todos_recibidos else "recibido_parcial"
    pedido.estado = estado_nuevo_pedido
    if todos_recibidos:
        pedido.fecha_recepcion = datetime.now(timezone.utc)
        
    db.commit()
    
    if estado_anterior_pedido != estado_nuevo_pedido:
        historial = HistorialEstado(
            pedido_id=pedido.id,
            estado_anterior=estado_anterior_pedido,
            estado_nuevo=estado_nuevo_pedido,
            usuario_id=user_data["usuario_id"],
            comentario=payload.observaciones or "Recepción registrada en bodega"
        )
        db.add(historial)
        db.commit()
        
    db.refresh(pedido)
    add_audit_task(background_tasks, "Registrar Recepcion", "POST", 200, 150, user_data["usuario_id"], f"Recepcion aplicada. Nuevo estado: {estado_nuevo_pedido}")
    
    return build_success_response(data=PedidoResponse.model_validate(pedido), message=f"Recepción procesada. Pedido en estado {estado_nuevo_pedido}")

@router.get("/{pedido_id}/historial", response_model=StandardResponse[list[HistorialEstadoResponse]])
async def consultar_historial(
    request: Request,
    background_tasks: BackgroundTasks,
    pedido_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user_data = await verify_user_session_and_permission(request, "PED_CONSULTAR_HISTORIAL")
    historial = db.query(HistorialEstado).filter(HistorialEstado.pedido_id == pedido_id).order_by(HistorialEstado.fecha_cambio.asc()).all()
    add_audit_task(background_tasks, "Consultar Historial", "GET", 200, 30, user_data["usuario_id"])
    return build_success_response(data=[HistorialEstadoResponse.model_validate(h) for h in historial], message="Historial de estados")
