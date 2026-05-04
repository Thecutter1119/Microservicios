from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Pedido(Base):
    __tablename__ = "ped_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(30), unique=True, nullable=False, index=True)
    solicitante_id = Column(BigInteger, nullable=False, index=True)
    proveedor_id = Column(BigInteger, nullable=False, index=True)
    estado = Column(String(20), nullable=False, default='borrador', index=True)
    fecha_solicitud = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    fecha_aprobacion = Column(DateTime(timezone=True), nullable=True)
    fecha_recepcion = Column(DateTime(timezone=True), nullable=True)
    monto_total = Column(Numeric(15, 2), nullable=False, default=0.00)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    historial_estados = relationship("HistorialEstado", back_populates="pedido", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("estado IN ('borrador', 'enviado', 'aprobado', 'en_proceso', 'recibido_parcial', 'recibido', 'cancelado')", name='chk_pedidos_estado'),
    )


class ItemPedido(Base):
    __tablename__ = "ped_items"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("ped_pedidos.id"), nullable=False, index=True)
    activo_id = Column(BigInteger, nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    cantidad_solicitada = Column(Numeric(10, 2), nullable=False)
    cantidad_recibida = Column(Numeric(10, 2), nullable=False, default=0.00)
    valor_unitario = Column(Numeric(15, 2), nullable=False)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.00)
    estado = Column(String(20), nullable=False, default='pendiente', index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    pedido = relationship("Pedido", back_populates="items")

    __table_args__ = (
        CheckConstraint('cantidad_solicitada > 0', name='chk_items_cant_solic'),
        CheckConstraint('cantidad_recibida >= 0', name='chk_items_cant_recib'),
        CheckConstraint('valor_unitario > 0', name='chk_items_valor_unit'),
        CheckConstraint("estado IN ('pendiente', 'recibido_parcial', 'recibido')", name='chk_items_estado'),
    )


class HistorialEstado(Base):
    __tablename__ = "ped_historial_estados"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("ped_pedidos.id"), nullable=False, index=True)
    estado_anterior = Column(String(20), nullable=True)
    estado_nuevo = Column(String(20), nullable=False)
    usuario_id = Column(BigInteger, nullable=False, index=True)
    fecha_cambio = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    comentario = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    pedido = relationship("Pedido", back_populates="historial_estados")
