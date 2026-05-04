from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class Calificacion(Base):
    __tablename__ = "calificaciones"
    __table_args__ = (UniqueConstraint("entrega_id", name="uq_calificaciones_entrega_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entrega_id: Mapped[int] = mapped_column(ForeignKey("entregas.id"), nullable=False, index=True)
    repartidor_id: Mapped[int] = mapped_column(ForeignKey("repartidores.id"), nullable=False, index=True)
    solicitante_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    puntaje: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    entrega: Mapped["Entrega"] = relationship(back_populates="calificaciones")
