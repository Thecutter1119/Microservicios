from app.infrastructure.database import Base, engine
from app.domain.models.calificacion import Calificacion
from app.domain.models.entrega import Entrega
from app.domain.models.repartidor import Repartidor
from app.domain.models.seguimiento import Seguimiento


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_all_tables()
