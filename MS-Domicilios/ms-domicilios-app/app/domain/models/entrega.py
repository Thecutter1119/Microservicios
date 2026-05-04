from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class EntregaEstado(str, Enum):
    PENDIENTE = "pendiente"
    ASIGNADA = "asignada"
    EN_CAMINO = "en_camino"
    ENTREGADA = "entregada"
    FALLIDA = "fallida"
    DEVUELTA = "devuelta"


class Entrega(Base):
    __tablename__ = "entregas"
    __table_args__ = (
        UniqueConstraint("pedido_id", name="uq_entregas_pedido_id"),
        Index("ix_entregas_estado_fecha", "estado", "fecha_creacion"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    repartidor_id: Mapped[int | None] = mapped_column(ForeignKey("repartidores.id"), nullable=True)
    origen: Mapped[str] = mapped_column(String(255), nullable=False)
    destino: Mapped[str] = mapped_column(String(255), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[EntregaEstado] = mapped_column(
        SqlEnum(
            EntregaEstado,
            name="entrega_estado",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=EntregaEstado.PENDIENTE,
    )
    costo_envio: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    repartidor: Mapped["Repartidor | None"] = relationship(back_populates="entregas")
    seguimientos: Mapped[list["Seguimiento"]] = relationship(back_populates="entrega")
    calificaciones: Mapped[list["Calificacion"]] = relationship(back_populates="entrega")
