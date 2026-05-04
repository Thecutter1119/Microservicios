from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class CategoriaIn(BaseModel):
    nombre: str
    descripcion: str | None = None
    categoria_padre_id: int | None = None
    estado: str = "activo"


class CategoriaOut(CategoriaIn):
    id: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ActivoIn(BaseModel):
    codigo_interno: str
    nombre: str
    descripcion: str | None = None
    categoria_id: int
    proveedor_id: int | None = None
    precio_adquisicion: float
    fecha_adquisicion: date
    vida_util_meses: int
    ubicacion_fisica: str | None = None
    estado: str = "disponible"
    stock_actual: int = 0
    stock_minimo: int = 0


class ActivoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    categoria_id: int | None = None
    proveedor_id: int | None = None
    precio_adquisicion: float | None = None
    fecha_adquisicion: date | None = None
    vida_util_meses: int | None = None
    ubicacion_fisica: str | None = None
    estado: str | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None


class ActivoOut(BaseModel):
    id: int
    codigo_interno: str
    nombre: str
    descripcion: str | None = None
    categoria_id: int
    proveedor_id: int | None = None
    precio_adquisicion: float
    fecha_adquisicion: date
    vida_util_meses: int
    valor_depreciacion_actual: float
    ubicacion_fisica: str | None = None
    estado: str
    stock_actual: int
    stock_minimo: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class MovimientoIn(BaseModel):
    activo_id: int
    tipo_movimiento: str
    cantidad: int
    motivo: str
    usuario_responsable_id: int | None = None
    pedido_referencia: str | None = None
