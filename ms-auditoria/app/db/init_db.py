from app.core.config import settings
from app.db.session import Base, SessionLocal, engine
from app.models.entities import ConfigRetencion, EstadisticaServicio, EventoLog  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(ConfigRetencion).first():
            db.add(ConfigRetencion(dias_retencion=settings.DEFAULT_RETENTION_DAYS, estado="activa"))
            db.commit()
    finally:
        db.close()
