import app.domain.models  # noqa: F401

from app.infrastructure.database import Base


def test_domain_tables_are_registered() -> None:
    table_names = set(Base.metadata.tables)

    assert {"repartidores", "entregas", "seguimientos", "calificaciones"}.issubset(table_names)
