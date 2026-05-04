from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.responses import build_success_response
from app.db.session import get_db
from app.models.entities import HistorialReintento, Notificacion, Plantilla, PreferenciaUsuario
from app.schemas.entities import NotificacionIn, NotificacionPlantillaIn, PlantillaIn, PreferenciaIn

router = APIRouter(tags=["ms-notificaciones"])

PRIORITY_ORDER = {"urgente": 0, "normal": 1, "baja": 2}


def _render_template(template: str, variables: dict[str, str]) -> str:
    text = template
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))
    return text


def _in_do_not_disturb(pref: PreferenciaUsuario | None) -> bool:
    if not pref or not pref.no_molestar_inicio or not pref.no_molestar_fin:
        return False
    now_t = datetime.utcnow().time()
    start = pref.no_molestar_inicio
    end = pref.no_molestar_fin
    if start <= end:
        return start <= now_t <= end
    return now_t >= start or now_t <= end


def _simulate_send(db: Session, notif: Notificacion) -> None:
    pref = db.query(PreferenciaUsuario).filter(PreferenciaUsuario.usuario_id == notif.usuario_id).first()
    if pref and not pref.notificaciones_activas:
        notif.estado = "fallida"
        db.add(HistorialReintento(notificacion_id=notif.id, numero_intento=notif.intentos + 1, resultado="fallo", detalle_error="Notificaciones desactivadas por usuario"))
        return
    if notif.prioridad in {"normal", "baja"} and _in_do_not_disturb(pref):
        # Se mantiene pendiente hasta que pase no molestar.
        return

    while notif.intentos < notif.max_intentos:
        notif.intentos += 1
        # En este proyecto el envio es simulado: se marca enviada en primer intento.
        notif.estado = "enviada"
        notif.fecha_envio = datetime.utcnow()
        db.add(HistorialReintento(notificacion_id=notif.id, numero_intento=notif.intentos, resultado="exito", detalle_error=None))
        break
    if notif.intentos >= notif.max_intentos and notif.estado != "enviada":
        notif.estado = "fallida"


@router.post("/plantillas")
def create_template(payload: PlantillaIn, db: Session = Depends(get_db)):
    if db.query(Plantilla).filter(Plantilla.nombre == payload.nombre).first():
        raise HTTPException(status_code=409, detail="Plantilla duplicada")
    row = Plantilla(
        nombre=payload.nombre,
        canal=payload.canal,
        asunto_template=payload.asunto_template,
        mensaje_template=payload.mensaje_template,
        variables_requeridas=",".join(payload.variables_requeridas or []),
        estado=payload.estado,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id}, message="Plantilla creada")


@router.get("/plantillas")
def list_templates(db: Session = Depends(get_db)):
    rows = db.query(Plantilla).order_by(Plantilla.id.desc()).all()
    data = [
        {
            "id": x.id,
            "nombre": x.nombre,
            "canal": x.canal,
            "asunto_template": x.asunto_template,
            "mensaje_template": x.mensaje_template,
            "variables_requeridas": (x.variables_requeridas or "").split(",") if x.variables_requeridas else [],
            "estado": x.estado,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Plantillas listadas")


@router.put("/plantillas/{plantilla_id}")
def update_template(plantilla_id: int, payload: PlantillaIn, db: Session = Depends(get_db)):
    row = db.query(Plantilla).filter(Plantilla.id == plantilla_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    row.nombre = payload.nombre
    row.canal = payload.canal
    row.asunto_template = payload.asunto_template
    row.mensaje_template = payload.mensaje_template
    row.variables_requeridas = ",".join(payload.variables_requeridas or [])
    row.estado = payload.estado
    db.commit()
    return build_success_response(data={"id": plantilla_id}, message="Plantilla actualizada")


@router.post("/plantillas/{plantilla_id}/desactivar")
def disable_template(plantilla_id: int, db: Session = Depends(get_db)):
    row = db.query(Plantilla).filter(Plantilla.id == plantilla_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    row.estado = "inactiva"
    db.commit()
    return build_success_response(data={"id": plantilla_id}, message="Plantilla desactivada")


@router.post("/preferencias")
def upsert_preference(payload: PreferenciaIn, db: Session = Depends(get_db)):
    row = db.query(PreferenciaUsuario).filter(PreferenciaUsuario.usuario_id == payload.usuario_id).first()
    if row:
        row.canal_preferido = payload.canal_preferido
        row.notificaciones_activas = payload.notificaciones_activas
        row.no_molestar_inicio = payload.no_molestar_inicio
        row.no_molestar_fin = payload.no_molestar_fin
    else:
        row = PreferenciaUsuario(**payload.model_dump())
        db.add(row)
    db.commit()
    return build_success_response(data={"usuario_id": payload.usuario_id}, message="Preferencias guardadas")


@router.get("/preferencias/{usuario_id}")
def get_preference(usuario_id: int, db: Session = Depends(get_db)):
    row = db.query(PreferenciaUsuario).filter(PreferenciaUsuario.usuario_id == usuario_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Preferencias no encontradas")
    data = {
        "usuario_id": row.usuario_id,
        "canal_preferido": row.canal_preferido,
        "notificaciones_activas": row.notificaciones_activas,
        "no_molestar_inicio": row.no_molestar_inicio.isoformat() if row.no_molestar_inicio else None,
        "no_molestar_fin": row.no_molestar_fin.isoformat() if row.no_molestar_fin else None,
    }
    return build_success_response(data=data, message="Preferencias consultadas")


@router.post("/enviar")
def send_notification(payload: NotificacionIn, db: Session = Depends(get_db)):
    notif = Notificacion(**payload.model_dump(), estado="pendiente")
    db.add(notif)
    db.commit()
    db.refresh(notif)
    _simulate_send(db, notif)
    db.commit()
    return build_success_response(data={"id": notif.id, "estado": notif.estado}, message="Notificacion procesada")


@router.post("/enviar-con-plantilla")
def send_with_template(payload: NotificacionPlantillaIn, db: Session = Depends(get_db)):
    tpl = db.query(Plantilla).filter(Plantilla.id == payload.plantilla_id, Plantilla.estado == "activo").first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada o inactiva")
    required = [x for x in (tpl.variables_requeridas or "").split(",") if x]
    missing = [x for x in required if x not in payload.variables]
    if missing:
        raise HTTPException(status_code=400, detail=f"Faltan variables requeridas: {missing}")
    asunto = _render_template(tpl.asunto_template or "", payload.variables) if tpl.asunto_template else None
    mensaje = _render_template(tpl.mensaje_template, payload.variables)
    notif = Notificacion(
        usuario_id=payload.usuario_id,
        canal=tpl.canal,
        asunto=asunto,
        mensaje=mensaje,
        prioridad=payload.prioridad,
        max_intentos=payload.max_intentos,
        request_id=payload.request_id,
        estado="pendiente",
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    _simulate_send(db, notif)
    db.commit()
    return build_success_response(data={"id": notif.id, "estado": notif.estado}, message="Notificacion con plantilla procesada")


@router.post("/enviar-masivo")
def send_massive(
    usuario_ids: list[int],
    canal: str,
    asunto: str | None,
    mensaje: str,
    prioridad: str = "normal",
    max_intentos: int = 3,
    request_id: str | None = None,
    db: Session = Depends(get_db),
):
    created = []
    for user_id in usuario_ids:
        notif = Notificacion(
            usuario_id=user_id,
            canal=canal,
            asunto=asunto,
            mensaje=mensaje,
            prioridad=prioridad,
            max_intentos=max_intentos,
            request_id=request_id,
            estado="pendiente",
        )
        db.add(notif)
        db.flush()
        _simulate_send(db, notif)
        created.append({"id": notif.id, "usuario_id": user_id, "estado": notif.estado})
    db.commit()
    return build_success_response(data={"notificaciones": created}, message="Envio masivo procesado")


@router.get("/pendientes")
def list_pending(db: Session = Depends(get_db)):
    rows = db.query(Notificacion).filter(Notificacion.estado == "pendiente").all()
    rows = sorted(rows, key=lambda x: PRIORITY_ORDER.get(x.prioridad, 99))
    data = [{"id": x.id, "usuario_id": x.usuario_id, "prioridad": x.prioridad, "estado": x.estado} for x in rows]
    return build_success_response(data=data, message="Notificaciones pendientes")


@router.post("/notificaciones/{notificacion_id}/leida")
def mark_read(notificacion_id: int, db: Session = Depends(get_db)):
    row = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    row.estado = "leida"
    row.fecha_lectura = datetime.utcnow()
    db.commit()
    return build_success_response(data={"id": notificacion_id}, message="Notificacion marcada como leida")


@router.get("/usuarios/{usuario_id}/no-leidas")
def unread_by_user(usuario_id: int, db: Session = Depends(get_db)):
    rows = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id, Notificacion.estado != "leida").order_by(Notificacion.id.desc()).all()
    data = [
        {
            "id": x.id,
            "canal": x.canal,
            "asunto": x.asunto,
            "mensaje": x.mensaje,
            "prioridad": x.prioridad,
            "estado": x.estado,
            "fecha_envio": x.fecha_envio.isoformat() if x.fecha_envio else None,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="No leidas del usuario")
