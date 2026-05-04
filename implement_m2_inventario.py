from pathlib import Path
from textwrap import dedent

ROOT = Path(r"c:\Users\jhons\Downloads\Microservicios")


def write(rel_path: str, content: str) -> None:
    file_path = ROOT / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


write(
    "ms-inventario/init_postgres.sql",
    dedent(
        """\
        CREATE DATABASE db_inventario;
        \\c db_inventario

        CREATE TABLE IF NOT EXISTS inv_categorias (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL UNIQUE,
            descripcion TEXT,
            categoria_padre_id INTEGER REFERENCES inv_categorias(id),
            estado VARCHAR(20) NOT NULL DEFAULT 'activo',
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS inv_activos (
            id SERIAL PRIMARY KEY,
            codigo_interno VARCHAR(60) NOT NULL UNIQUE,
            nombre VARCHAR(180) NOT NULL,
            descripcion TEXT,
            categoria_id INTEGER NOT NULL REFERENCES inv_categorias(id),
            proveedor_id INTEGER,
            precio_adquisicion NUMERIC(14,2) NOT NULL,
            fecha_adquisicion DATE NOT NULL,
            vida_util_meses INTEGER NOT NULL,
            valor_depreciacion_actual NUMERIC(14,2) NOT NULL DEFAULT 0,
            ubicacion_fisica VARCHAR(180),
            estado VARCHAR(30) NOT NULL DEFAULT 'disponible',
            stock_actual INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS inv_movimientos_stock (
            id SERIAL PRIMARY KEY,
            activo_id INTEGER NOT NULL REFERENCES inv_activos(id),
            tipo_movimiento VARCHAR(20) NOT NULL,
            cantidad INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            usuario_responsable_id INTEGER,
            pedido_referencia VARCHAR(80),
            request_id VARCHAR(80),
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
    ),
)

write(
    "ms-inventario/app/models/entities.py",
    dedent(
        """\
        from datetime import date
        from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
        from sqlalchemy.orm import Mapped, mapped_column

        from app.db.session import Base


        class Categoria(Base):
            __tablename__ = "inv_categorias"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            categoria_padre_id: Mapped[int | None] = mapped_column(ForeignKey("inv_categorias.id"), nullable=True)
            estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)
            created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())


        class Activo(Base):
            __tablename__ = "inv_activos"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            codigo_interno: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
            nombre: Mapped[str] = mapped_column(String(180), nullable=False)
            descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
            categoria_id: Mapped[int] = mapped_column(ForeignKey("inv_categorias.id"), nullable=False)
            proveedor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
            precio_adquisicion: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
            fecha_adquisicion: Mapped[date] = mapped_column(Date, nullable=False)
            vida_util_meses: Mapped[int] = mapped_column(Integer, nullable=False)
            valor_depreciacion_actual: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
            ubicacion_fisica: Mapped[str | None] = mapped_column(String(180), nullable=True)
            estado: Mapped[str] = mapped_column(String(30), default="disponible", nullable=False)
            stock_actual: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            stock_minimo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
            created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
            updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


        class MovimientoStock(Base):
            __tablename__ = "inv_movimientos_stock"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
            activo_id: Mapped[int] = mapped_column(ForeignKey("inv_activos.id"), nullable=False, index=True)
            tipo_movimiento: Mapped[str] = mapped_column(String(20), nullable=False)
            cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
            motivo: Mapped[str] = mapped_column(Text, nullable=False)
            usuario_responsable_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
            pedido_referencia: Mapped[str | None] = mapped_column(String(80), nullable=True)
            request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
            created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=False), server_default=func.now())
        """
    ),
)

write(
    "ms-inventario/app/schemas/entities.py",
    dedent(
        """\
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
        """
    ),
)

write(
    "ms-inventario/app/api/routes/entities.py",
    dedent(
        """\
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
        """
    ),
)

print("ms-inventario implementado.")
