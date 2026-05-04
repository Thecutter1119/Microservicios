from pydantic import BaseModel


class CategoriaIn(BaseModel):
    nombre: str
    descripcion: str | None = None
    requiere_aprobacion_especial: bool = False
    estado: str = "activo"


class GastoIn(BaseModel):
    descripcion: str
    monto: float
    categoria_id: int
    partida_presupuestal_id: int
    proveedor_id: int | None = None
    solicitado_por: int | None = None
    observaciones: str | None = None


class GastoUpdate(BaseModel):
    descripcion: str | None = None
    monto: float | None = None
    categoria_id: int | None = None
    partida_presupuestal_id: int | None = None
    proveedor_id: int | None = None
    observaciones: str | None = None


class NovedadIn(BaseModel):
    gasto_id: int
    tipo_novedad: str
    descripcion: str
    monto_impacto: float
    reportado_por: int | None = None


class NovedadUpdate(BaseModel):
    descripcion: str | None = None
    monto_impacto: float | None = None
    estado: str | None = None
