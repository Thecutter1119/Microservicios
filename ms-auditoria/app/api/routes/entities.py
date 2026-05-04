from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.responses import build_success_response
from app.db.session import get_db
from app.models.entities import ConfigRetencion, EstadisticaServicio, EventoLog
from app.schemas.entities import EventoIn, RetencionIn

router = APIRouter(tags=["ms-auditoria"])


def _save_logs_sync(db: Session, events: list[EventoIn]) -> None:
    for ev in events:
        db.add(EventoLog(**ev.model_dump()))
    db.commit()


@router.post("/logs")
def ingest_logs(payload: list[EventoIn], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not payload:
        raise HTTPException(status_code=400, detail="Payload vacio")
    # Fire-and-forget: responde y procesa en segundo plano.
    background_tasks.add_task(_save_logs_sync, db, payload)
    return build_success_response(data={"recibidos": len(payload)}, message="Logs recibidos para procesamiento")


@router.post("/log")
def ingest_log(payload: EventoIn, db: Session = Depends(get_db)):
    db.add(EventoLog(**payload.model_dump()))
    db.commit()
    return build_success_response(data={"ok": True}, message="Log almacenado")


@router.get("/traza/{request_id}")
def trace_by_request_id(request_id: str, page: int = Query(default=1, ge=1), size: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    query = db.query(EventoLog).filter(EventoLog.request_id == request_id).order_by(EventoLog.fecha_hora.asc())
    total = query.count()
    rows = query.offset((page - 1) * size).limit(size).all()
    data = [
        {
            "fecha_hora": x.fecha_hora.isoformat() if x.fecha_hora else None,
            "request_id": x.request_id,
            "microservicio": x.microservicio,
            "funcionalidad": x.funcionalidad,
            "metodo": x.metodo,
            "codigo_respuesta": x.codigo_respuesta,
            "duracion_ms": x.duracion_ms,
            "usuario_id": x.usuario_id,
            "detalle": x.detalle,
        }
        for x in rows
    ]
    return build_success_response(data={"items": data, "total": total, "page": page, "size": size}, message="Traza por request_id")


@router.get("/logs")
def search_logs(
    microservicio: str | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(EventoLog)
    if microservicio:
        query = query.filter(EventoLog.microservicio == microservicio)
    if fecha_inicio:
        query = query.filter(EventoLog.fecha_hora >= fecha_inicio)
    if fecha_fin:
        query = query.filter(EventoLog.fecha_hora <= fecha_fin)
    total = query.count()
    rows = query.order_by(EventoLog.fecha_hora.desc()).offset((page - 1) * size).limit(size).all()
    data = [
        {
            "id": x.id,
            "fecha_hora": x.fecha_hora.isoformat() if x.fecha_hora else None,
            "request_id": x.request_id,
            "microservicio": x.microservicio,
            "funcionalidad": x.funcionalidad,
            "metodo": x.metodo,
            "codigo_respuesta": x.codigo_respuesta,
            "duracion_ms": x.duracion_ms,
            "usuario_id": x.usuario_id,
            "detalle": x.detalle,
        }
        for x in rows
    ]
    return build_success_response(data={"items": data, "total": total, "page": page, "size": size}, message="Busqueda de logs")


@router.get("/retencion")
def get_retention(db: Session = Depends(get_db)):
    row = db.query(ConfigRetencion).first()
    if not row:
        raise HTTPException(status_code=404, detail="Configuracion de retencion no encontrada")
    return build_success_response(
        data={
            "dias_retencion": row.dias_retencion,
            "estado": row.estado,
            "ultima_rotacion": row.ultima_rotacion.isoformat() if row.ultima_rotacion else None,
            "registros_eliminados_ultima_rotacion": row.registros_eliminados_ultima_rotacion,
        },
        message="Configuracion de retencion",
    )


@router.put("/retencion")
def update_retention(payload: RetencionIn, db: Session = Depends(get_db)):
    row = db.query(ConfigRetencion).first()
    if not row:
        row = ConfigRetencion()
        db.add(row)
    row.dias_retencion = payload.dias_retencion
    row.estado = payload.estado
    db.commit()
    return build_success_response(data={"dias_retencion": row.dias_retencion, "estado": row.estado}, message="Retencion actualizada")


@router.post("/rotacion/ejecutar")
def rotate_logs(db: Session = Depends(get_db)):
    cfg = db.query(ConfigRetencion).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuracion de retencion no encontrada")
    cutoff = datetime.utcnow() - timedelta(days=cfg.dias_retencion)
    to_delete = db.query(EventoLog).filter(EventoLog.fecha_hora < cutoff)
    count = to_delete.count()
    to_delete.delete(synchronize_session=False)
    cfg.ultima_rotacion = datetime.utcnow()
    cfg.registros_eliminados_ultima_rotacion = count
    db.commit()
    return build_success_response(data={"registros_eliminados": count}, message="Rotacion ejecutada")


@router.post("/estadisticas/recalcular")
def recalc_stats(periodo: str = "diario", db: Session = Depends(get_db)):
    # Simplificado: calcula sobre todos los registros actuales por microservicio.
    rows = db.query(EventoLog.microservicio).distinct().all()
    now_date = datetime.utcnow().date()
    created = 0
    for row in rows:
        micro = row[0]
        logs = db.query(EventoLog).filter(EventoLog.microservicio == micro).all()
        if not logs:
            continue
        total = len(logs)
        errors = sum(1 for l in logs if (l.codigo_respuesta or 200) >= 400)
        avg = sum((l.duracion_ms or 0) for l in logs) / total
        freq = {}
        for l in logs:
            key = l.funcionalidad or "N/A"
            freq[key] = freq.get(key, 0) + 1
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[0][0]
        db.add(
            EstadisticaServicio(
                microservicio=micro,
                periodo=periodo,
                fecha=now_date,
                total_peticiones=total,
                total_errores=errors,
                tiempo_promedio_ms=avg,
                funcionalidad_mas_utilizada=top,
            )
        )
        created += 1
    db.commit()
    return build_success_response(data={"estadisticas_generadas": created}, message="Estadisticas recalculadas")


@router.get("/estadisticas")
def get_stats(microservicio: str | None = None, page: int = Query(default=1, ge=1), size: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    query = db.query(EstadisticaServicio)
    if microservicio:
        query = query.filter(EstadisticaServicio.microservicio == microservicio)
    total = query.count()
    rows = query.order_by(EstadisticaServicio.id.desc()).offset((page - 1) * size).limit(size).all()
    data = [
        {
            "id": x.id,
            "microservicio": x.microservicio,
            "periodo": x.periodo,
            "fecha": x.fecha.isoformat() if x.fecha else None,
            "total_peticiones": x.total_peticiones,
            "total_errores": x.total_errores,
            "tiempo_promedio_ms": float(x.tiempo_promedio_ms),
            "funcionalidad_mas_utilizada": x.funcionalidad_mas_utilizada,
            "fecha_calculo": x.fecha_calculo.isoformat() if x.fecha_calculo else None,
        }
        for x in rows
    ]
    return build_success_response(data={"items": data, "total": total, "page": page, "size": size}, message="Estadisticas consultadas")
