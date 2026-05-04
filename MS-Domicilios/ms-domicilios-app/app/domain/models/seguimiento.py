from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class SeguimientoTipo(str, Enum):
    MANUAL = "manual"
    AUTOMATICO = "automatico"


class Seguimiento(Base):
    __tablename__ = "seguimientos"
    __table_args__ = (Index("ix_seguimientos_entrega_fecha", "entrega_id", "fecha_registro"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entrega_id: Mapped[int] = mapped_column(ForeignKey("entregas.id"), nullable=False, index=True)
    tipo: Mapped[SeguimientoTipo] = mapped_column(
        SqlEnum(
            SeguimientoTipo,
            name="seguimiento_tipo",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=SeguimientoTipo.MANUAL,
    )
    latitud: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitud: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    entrega: Mapped["Entrega"] = relationship(back_populates="seguimientos")
