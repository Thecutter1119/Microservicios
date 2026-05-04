"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-06 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    repartidor_estado = sa.Enum("disponible", "en_ruta", "inactivo", name="repartidor_estado")
    entrega_estado = sa.Enum(
        "pendiente", "asignada", "en_camino", "entregada", "fallida", "devuelta", name="entrega_estado"
    )
    seguimiento_tipo = sa.Enum("manual", "automatico", name="seguimiento_tipo")

    op.create_table(
        "repartidores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=False),
        sa.Column("tipo_vehiculo", sa.String(length=50), nullable=False),
        sa.Column("placa_vehiculo", sa.String(length=20), nullable=False),
        sa.Column("zona_cobertura", sa.String(length=120), nullable=False),
        sa.Column("estado", repartidor_estado, nullable=False),
        sa.Column("calificacion_promedio", sa.Numeric(3, 2), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repartidores")),
        sa.UniqueConstraint("placa_vehiculo", name="uq_repartidores_placa_vehiculo"),
    )
    op.create_index(op.f("ix_repartidores_usuario_id"), "repartidores", ["usuario_id"], unique=False)
    op.create_index(op.f("ix_repartidores_zona_cobertura"), "repartidores", ["zona_cobertura"], unique=False)

    op.create_table(
        "entregas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("repartidor_id", sa.Integer(), nullable=True),
        sa.Column("origen", sa.String(length=255), nullable=False),
        sa.Column("destino", sa.String(length=255), nullable=False),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("estado", entrega_estado, nullable=False),
        sa.Column("costo_envio", sa.Numeric(10, 2), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entregas")),
        sa.ForeignKeyConstraint(["repartidor_id"], ["repartidores.id"]),
        sa.UniqueConstraint("pedido_id", name="uq_entregas_pedido_id"),
    )
    op.create_index(op.f("ix_entregas_pedido_id"), "entregas", ["pedido_id"], unique=False)
    op.create_index(op.f("ix_entregas_repartidor_id"), "entregas", ["repartidor_id"], unique=False)
    op.create_index("ix_entregas_estado_fecha", "entregas", ["estado", "fecha_creacion"], unique=False)

    op.create_table(
        "seguimientos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entrega_id", sa.Integer(), nullable=False),
        sa.Column("tipo", seguimiento_tipo, nullable=False),
        sa.Column("latitud", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitud", sa.Numeric(9, 6), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_seguimientos")),
        sa.ForeignKeyConstraint(["entrega_id"], ["entregas.id"]),
    )
    op.create_index(op.f("ix_seguimientos_entrega_id"), "seguimientos", ["entrega_id"], unique=False)
    op.create_index("ix_seguimientos_entrega_fecha", "seguimientos", ["entrega_id", "fecha_registro"], unique=False)

    op.create_table(
        "calificaciones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entrega_id", sa.Integer(), nullable=False),
        sa.Column("repartidor_id", sa.Integer(), nullable=False),
        sa.Column("solicitante_id", sa.Integer(), nullable=False),
        sa.Column("puntaje", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_calificaciones")),
        sa.ForeignKeyConstraint(["entrega_id"], ["entregas.id"]),
        sa.ForeignKeyConstraint(["repartidor_id"], ["repartidores.id"]),
        sa.UniqueConstraint("entrega_id", name="uq_calificaciones_entrega_id"),
    )
    op.create_index(op.f("ix_calificaciones_entrega_id"), "calificaciones", ["entrega_id"], unique=False)
    op.create_index(op.f("ix_calificaciones_repartidor_id"), "calificaciones", ["repartidor_id"], unique=False)
    op.create_index(op.f("ix_calificaciones_solicitante_id"), "calificaciones", ["solicitante_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_calificaciones_solicitante_id"), table_name="calificaciones")
    op.drop_index(op.f("ix_calificaciones_repartidor_id"), table_name="calificaciones")
    op.drop_index(op.f("ix_calificaciones_entrega_id"), table_name="calificaciones")
    op.drop_table("calificaciones")

    op.drop_index("ix_seguimientos_entrega_fecha", table_name="seguimientos")
    op.drop_index(op.f("ix_seguimientos_entrega_id"), table_name="seguimientos")
    op.drop_table("seguimientos")

    op.drop_index("ix_entregas_estado_fecha", table_name="entregas")
    op.drop_index(op.f("ix_entregas_repartidor_id"), table_name="entregas")
    op.drop_index(op.f("ix_entregas_pedido_id"), table_name="entregas")
    op.drop_table("entregas")

    op.drop_index(op.f("ix_repartidores_zona_cobertura"), table_name="repartidores")
    op.drop_index(op.f("ix_repartidores_usuario_id"), table_name="repartidores")
    op.drop_table("repartidores")

    op.execute(sa.text("DROP TYPE IF EXISTS seguimiento_tipo"))
    op.execute(sa.text("DROP TYPE IF EXISTS entrega_estado"))
    op.execute(sa.text("DROP TYPE IF EXISTS repartidor_estado"))
