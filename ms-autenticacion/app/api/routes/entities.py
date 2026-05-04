from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.middleware import get_current_request_id
from app.core.responses import build_success_response
from app.core.security import build_jwt, decrypt_aes_base64, encrypt_aes_base64, verify_password
from app.db.session import get_db
from app.models.entities import HistorialAcceso, IntentoLogin, Sesion, TokenAplicacion
from app.schemas.entities import AppTokenIn, LoginIn, LogoutIn, ValidateSessionIn

router = APIRouter(tags=["ms-autenticacion"])


async def _get_user_for_login(login: str) -> dict:
    async with httpx.AsyncClient(timeout=4.0) as client:
        if "@" in login:
            r = await client.get(f"{settings.USR_BASE_URL}/api/v1/usuarios/internal/email/{login}")
        else:
            r = await client.get(f"{settings.USR_BASE_URL}/api/v1/usuarios/internal/username/{login}")
        r.raise_for_status()
        return r.json()["data"]


async def _get_roles_and_permissions(usuario_id: int) -> tuple[list[str], list[str]]:
    async with httpx.AsyncClient(timeout=4.0) as client:
        roles_r = await client.get(f"{settings.ROL_BASE_URL}/api/v1/usuarios/{usuario_id}/roles")
        roles_r.raise_for_status()
        roles_data = roles_r.json()["data"]
        role_names = [x["nombre"] for x in roles_data]
        perms_r = await client.get(f"{settings.ROL_BASE_URL}/api/v1/internal/usuarios/{usuario_id}/permisos")
        perms_r.raise_for_status()
        permisos = perms_r.json()["data"]["permisos"]
        return role_names, permisos


def _add_access_log(db: Session, usuario_id: int | None, tipo_evento: str, request: Request) -> None:
    db.add(
        HistorialAcceso(
            usuario_id=usuario_id,
            tipo_evento=tipo_evento,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=get_current_request_id(),
        )
    )
    db.commit()


@router.post("/login")
async def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    tracker = db.query(IntentoLogin).filter(IntentoLogin.login_key == payload.login).first()
    if tracker and tracker.bloqueado:
        _add_access_log(db, None, "bloqueo_cuenta", request)
        raise HTTPException(status_code=423, detail="Cuenta bloqueada por intentos fallidos")

    try:
        user_data = await _get_user_for_login(payload.login)
    except Exception:
        user_data = None

    if not user_data:
        if not tracker:
            tracker = IntentoLogin(login_key=payload.login, intentos=1, bloqueado=False)
            db.add(tracker)
        else:
            tracker.intentos += 1
            if tracker.intentos >= 5:
                tracker.bloqueado = True
        db.commit()
        _add_access_log(db, None, "intento_fallido", request)
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    if user_data["estado"] != "activo":
        raise HTTPException(status_code=403, detail="Usuario no activo")

    plain = decrypt_aes_base64(payload.password_encrypted)
    ok = verify_password(plain, user_data["password_hash"])
    if not ok:
        if not tracker:
            tracker = IntentoLogin(login_key=payload.login, intentos=1, bloqueado=False)
            db.add(tracker)
        else:
            tracker.intentos += 1
            if tracker.intentos >= 5:
                tracker.bloqueado = True
        db.commit()
        _add_access_log(db, user_data["id"], "intento_fallido", request)
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    if tracker:
        tracker.intentos = 0
        tracker.bloqueado = False
        db.commit()

    roles, permisos = await _get_roles_and_permissions(user_data["id"])
    jwt_token = build_jwt(user_data["id"], roles, permisos)
    session = Sesion(
        usuario_id=user_data["id"],
        token_jwt=jwt_token,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        estado="activa",
    )
    db.add(session)
    db.commit()
    _add_access_log(db, user_data["id"], "inicio_sesion", request)
    return build_success_response(data={"token": jwt_token, "usuario_id": user_data["id"], "roles": roles, "permisos": permisos}, message="Login exitoso")


@router.post("/logout")
def logout(payload: LogoutIn, request: Request, db: Session = Depends(get_db)):
    row = db.query(Sesion).filter(Sesion.token_jwt == payload.token, Sesion.estado == "activa").first()
    if not row:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")
    row.estado = "cerrada"
    row.last_activity_at = datetime.utcnow()
    db.commit()
    _add_access_log(db, row.usuario_id, "cierre_sesion", request)
    return build_success_response(data={"usuario_id": row.usuario_id}, message="Sesion cerrada")


@router.post("/validar-sesion")
def validate_session(payload: ValidateSessionIn, db: Session = Depends(get_db)):
    row = db.query(Sesion).filter(Sesion.token_jwt == payload.token, Sesion.estado == "activa").first()
    if not row:
        return build_success_response(data={"activa": False}, message="Sesion invalida")
    row.last_activity_at = datetime.utcnow()
    db.commit()
    return build_success_response(data={"activa": True, "usuario_id": row.usuario_id}, message="Sesion valida")


@router.get("/sesiones/activas")
def active_sessions(usuario_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Sesion).filter(Sesion.estado == "activa")
    if usuario_id:
        query = query.filter(Sesion.usuario_id == usuario_id)
    rows = query.order_by(Sesion.created_at.desc()).all()
    data = [
        {
            "id": x.id,
            "usuario_id": x.usuario_id,
            "ip": x.ip,
            "user_agent": x.user_agent,
            "created_at": x.created_at.isoformat() if x.created_at else None,
            "last_activity_at": x.last_activity_at.isoformat() if x.last_activity_at else None,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Sesiones activas listadas")


@router.post("/sesiones/{sesion_id}/forzar-cierre")
def force_close_session(sesion_id: int, db: Session = Depends(get_db)):
    row = db.query(Sesion).filter(Sesion.id == sesion_id, Sesion.estado == "activa").first()
    if not row:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")
    row.estado = "cerrada"
    db.commit()
    return build_success_response(data={"sesion_id": sesion_id}, message="Sesion cerrada por administrador")


@router.get("/historial-accesos")
def access_history(
    usuario_id: int | None = None,
    tipo_evento: str | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(HistorialAcceso)
    if usuario_id:
        query = query.filter(HistorialAcceso.usuario_id == usuario_id)
    if tipo_evento:
        query = query.filter(HistorialAcceso.tipo_evento == tipo_evento)
    if fecha_inicio:
        query = query.filter(HistorialAcceso.event_at >= fecha_inicio)
    if fecha_fin:
        query = query.filter(HistorialAcceso.event_at <= fecha_fin)
    rows = query.order_by(HistorialAcceso.event_at.desc()).all()
    data = [
        {
            "usuario_id": x.usuario_id,
            "tipo_evento": x.tipo_evento,
            "ip": x.ip,
            "user_agent": x.user_agent,
            "request_id": x.request_id,
            "event_at": x.event_at.isoformat() if x.event_at else None,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Historial de accesos")


@router.post("/tokens-aplicacion")
def create_app_token(payload: AppTokenIn, db: Session = Depends(get_db)):
    if db.query(TokenAplicacion).filter(TokenAplicacion.service_name == payload.service_name).first():
        raise HTTPException(status_code=409, detail="Token de aplicacion ya existe para ese servicio")
    row = TokenAplicacion(
        service_name=payload.service_name,
        token_encrypted=encrypt_aes_base64(payload.token_plain),
        descripcion=payload.descripcion,
        estado="activo",
        updated_by=payload.updated_by,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id, "service_name": row.service_name, "estado": row.estado}, message="Token de aplicacion creado")


@router.get("/tokens-aplicacion")
def list_app_tokens(db: Session = Depends(get_db)):
    rows = db.query(TokenAplicacion).order_by(TokenAplicacion.service_name.asc()).all()
    data = [
        {
            "id": x.id,
            "service_name": x.service_name,
            "descripcion": x.descripcion,
            "estado": x.estado,
            "created_at": x.created_at.isoformat() if x.created_at else None,
            "updated_at": x.updated_at.isoformat() if x.updated_at else None,
            "updated_by": x.updated_by,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Tokens de aplicacion listados")


@router.put("/tokens-aplicacion/{token_id}")
def update_app_token(token_id: int, payload: AppTokenIn, db: Session = Depends(get_db)):
    row = db.query(TokenAplicacion).filter(TokenAplicacion.id == token_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Token de aplicacion no encontrado")
    row.service_name = payload.service_name
    row.token_encrypted = encrypt_aes_base64(payload.token_plain)
    row.descripcion = payload.descripcion
    row.updated_by = payload.updated_by
    db.commit()
    return build_success_response(data={"id": row.id}, message="Token de aplicacion actualizado")


@router.post("/tokens-aplicacion/{token_id}/desactivar")
def deactivate_app_token(token_id: int, db: Session = Depends(get_db)):
    row = db.query(TokenAplicacion).filter(TokenAplicacion.id == token_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Token de aplicacion no encontrado")
    row.estado = "inactivo"
    db.commit()
    return build_success_response(data={"id": row.id}, message="Token de aplicacion desactivado")
