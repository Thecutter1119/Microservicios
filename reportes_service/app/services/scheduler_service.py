"""
ms-reportes [REP] — Scheduler Interno (APScheduler)
REP-RF-019: Ejecutar Automáticamente Reportes Programados
Proceso no-HTTP; actor: ⚙️ Scheduler Interno.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings

log = logging.getLogger("ms-reportes.scheduler")

scheduler = AsyncIOScheduler(timezone="UTC")


def start_scheduler() -> None:
    """Inicia el scheduler con el intervalo configurado (default: 1 min)."""
    from app.services.programacion_service import ejecutar_programaciones_vencidas

    scheduler.add_job(
        ejecutar_programaciones_vencidas,
        trigger=IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
        id="rep_scheduler_principal",
        name="REP-RF-019 — Ejecución automática de reportes programados",
        replace_existing=True,
        misfire_grace_time=60,
    )
    scheduler.start()
    log.info(
        "Scheduler iniciado — intervalo: %d min",
        settings.SCHEDULER_INTERVAL_MINUTES,
    )


def stop_scheduler() -> None:
    """Detiene el scheduler limpiamente en el shutdown del servidor."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        log.info("Scheduler detenido")
