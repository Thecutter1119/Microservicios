from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.domain.models.entrega import Entrega


class RepartidorEstado(str, Enum):
    DISPONIBLE = "disponible"
    EN_RUTA = "en_ruta"
    INACTIVO = "inactivo"


class Repartidor(Base):
    __tablename__ = "repartidores"
    __table_args__ = (UniqueConstraint("placa_vehiculo", name="uq_repartidores_placa_vehiculo"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    tipo_vehiculo: Mapped[str] = mapped_column(String(50), nullable=False)
    placa_vehiculo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    zona_cobertura: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    estado: Mapped[RepartidorEstado] = mapped_column(
        SqlEnum(
            RepartidorEstado,
            name="repartidor_estado",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=RepartidorEstado.DISPONIBLE,
    )
    calificacion_promedio: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    entregas: Mapped[list["Entrega"]] = relationship(back_populates="repartidor")
