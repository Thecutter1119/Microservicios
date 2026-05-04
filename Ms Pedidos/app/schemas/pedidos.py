from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ORMBaseModel(BaseModel):
    model_config = {"from_attributes": True}

class PedidoCreate(BaseModel):
    proveedor_id: int
    observaciones: Optional[str] = None

class PedidoUpdate(BaseModel):
    proveedor_id: Optional[int] = None
    observaciones: Optional[str] = None

class PedidoAvanzarEstado(BaseModel):
    comentario: str = Field(..., description="Comentario obligatorio para avanzar de estado")

class PedidoCancelar(BaseModel):
    motivo: str = Field(..., description="Motivo obligatorio para cancelar el pedido")

class PedidoResponse(ORMBaseModel):
    id: int
    numero_pedido: str
    solicitante_id: int
    proveedor_id: int
    estado: str
    fecha_solicitud: datetime
    fecha_aprobacion: Optional[datetime] = None
    fecha_recepcion: Optional[datetime] = None
    monto_total: float
    observaciones: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ItemPedidoCreate(BaseModel):
    activo_id: int
    descripcion: str
    cantidad_solicitada: float = Field(..., gt=0)
    valor_unitario: float = Field(..., gt=0)

class ItemPedidoUpdate(BaseModel):
    descripcion: Optional[str] = None
    cantidad_solicitada: Optional[float] = Field(None, gt=0)
    valor_unitario: Optional[float] = Field(None, gt=0)

class RecepcionItem(BaseModel):
    item_id: int
    cantidad_recibida: float = Field(..., gt=0)

class RegistroRecepcion(BaseModel):
    items: List[RecepcionItem]
    observaciones: Optional[str] = None

class ItemPedidoResponse(ORMBaseModel):
    id: int
    pedido_id: int
    activo_id: int
    descripcion: str
    cantidad_solicitada: float
    cantidad_recibida: float
    valor_unitario: float
    subtotal: float
    estado: str
    created_at: datetime
    updated_at: datetime

class PedidoDetalleResponse(PedidoResponse):
    items: List[ItemPedidoResponse] = []

class HistorialEstadoResponse(ORMBaseModel):
    id: int
    pedido_id: int
    estado_anterior: Optional[str]
    estado_nuevo: str
    usuario_id: int
    fecha_cambio: datetime
    comentario: Optional[str]
