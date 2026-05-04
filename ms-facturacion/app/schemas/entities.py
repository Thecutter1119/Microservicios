from datetime import datetime
from pydantic import BaseModel


class ConceptoIn(BaseModel):
    nombre: str
    descripcion: str | None = None
    valor_base: float
    es_recurrente: bool = False
    periodicidad: str | None = None
    estado: str = "activo"


class FacturaDetalleIn(BaseModel):
    concepto_id: int
    descripcion: str | None = None
    cantidad: int
    valor_unitario: float


class FacturaIn(BaseModel):
    usuario_id: int
    fecha_vencimiento: datetime
    porcentaje_impuesto: float = 0
    observaciones: str | None = None
    detalles: list[FacturaDetalleIn]
