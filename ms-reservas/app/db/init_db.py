from app.db.session import Base, SessionLocal, engine
from app.models.entities import BloqueoEspacio, PoliticaReserva, Reserva  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(PoliticaReserva).filter(PoliticaReserva.nombre == "Politica General").first():
            db.add(
                PoliticaReserva(
                    nombre="Politica General",
                    min_anticipacion_horas=2,
                    max_anticipacion_dias=60,
                    duracion_max_horas=8,
                    limite_cancelacion_horas=1,
                    max_reservas_activas_usuario=3,
                    estado="activo",
                )
            )
            db.commit()
    finally:
        db.close()
