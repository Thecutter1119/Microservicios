import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.responses import build_success_response
from app.core.security import decrypt_aes_base64, hash_password
from app.db.session import get_db
from app.models.entities import HistorialEstado, Perfil, Usuario
from app.schemas.entities import CambioEstadoIn, PerfilCreate, PerfilOut, PerfilUpdate, UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["ms-usuarios"])


def _user_to_out(user: Usuario) -> dict:
    return UsuarioOut.model_validate(user).model_dump(mode="json")


@router.post("")
def create_user(payload: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(or_(Usuario.username == payload.username, Usuario.email == payload.email)).first():
        raise HTTPException(status_code=409, detail="Usuario o correo ya existe")
    if payload.password:
        plain = payload.password
    elif payload.password_encrypted:
        try:
            plain = decrypt_aes_base64(payload.password_encrypted)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Password encrypted invalida") from exc
    else:
        raise HTTPException(status_code=400, detail="Debe enviar password o password_encrypted")
    if len(plain.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="La password no puede superar 72 bytes para bcrypt")
    user = Usuario(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(plain),
        rol_principal_id=payload.rol_principal_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(HistorialEstado(usuario_id=user.id, estado_anterior=None, estado_nuevo=user.estado, motivo="Creacion de usuario"))
    db.commit()
    return build_success_response(data=_user_to_out(user), message="Usuario creado")


@router.get("")
def list_users(db: Session = Depends(get_db)):
    rows = db.query(Usuario).order_by(Usuario.id.desc()).all()
    return build_success_response(data=[_user_to_out(x) for x in rows], message="Usuarios listados")


@router.get("/{usuario_id}")
def get_user(usuario_id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return build_success_response(data=_user_to_out(user), message="Usuario consultado")


@router.put("/{usuario_id}")
def update_user(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return build_success_response(data=_user_to_out(user), message="Usuario actualizado")


@router.post("/{usuario_id}/desactivar")
def deactivate_user(usuario_id: int, motivo: str = Query(...), changed_by: int | None = Query(default=None), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    anterior = user.estado
    user.estado = "inactivo"
    db.add(HistorialEstado(usuario_id=usuario_id, estado_anterior=anterior, estado_nuevo="inactivo", motivo=motivo, changed_by=changed_by))
    db.commit()
    return build_success_response(data={"usuario_id": usuario_id}, message="Usuario desactivado")


@router.post("/{usuario_id}/estado")
def change_state(usuario_id: int, payload: CambioEstadoIn, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    anterior = user.estado
    user.estado = payload.estado_nuevo
    db.add(HistorialEstado(
        usuario_id=usuario_id,
        estado_anterior=anterior,
        estado_nuevo=payload.estado_nuevo,
        motivo=payload.motivo,
        changed_by=payload.changed_by,
    ))
    db.commit()
    db.refresh(user)
    return build_success_response(data=_user_to_out(user), message="Estado actualizado")


@router.get("/{usuario_id}/historial-estados")
def state_history(usuario_id: int, db: Session = Depends(get_db)):
    rows = db.query(HistorialEstado).filter(HistorialEstado.usuario_id == usuario_id).order_by(HistorialEstado.changed_at.desc()).all()
    data = [
        {
            "id": x.id,
            "estado_anterior": x.estado_anterior,
            "estado_nuevo": x.estado_nuevo,
            "motivo": x.motivo,
            "changed_by": x.changed_by,
            "changed_at": x.changed_at.isoformat() if x.changed_at else None,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Historial consultado")


@router.post("/perfiles")
def create_profile(payload: PerfilCreate, db: Session = Depends(get_db)):
    if not db.query(Usuario).filter(Usuario.id == payload.usuario_id).first():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if payload.numero_documento and db.query(Perfil).filter(Perfil.numero_documento == payload.numero_documento).first():
        raise HTTPException(status_code=409, detail="Numero de documento duplicado")
    row = Perfil(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data=PerfilOut.model_validate(row).model_dump(mode="json"), message="Perfil creado")


@router.get("/{usuario_id}/perfil")
def get_profile(usuario_id: int, db: Session = Depends(get_db)):
    row = db.query(Perfil).filter(Perfil.usuario_id == usuario_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return build_success_response(data=PerfilOut.model_validate(row).model_dump(mode="json"), message="Perfil consultado")


@router.put("/{usuario_id}/perfil")
def update_profile(usuario_id: int, payload: PerfilUpdate, db: Session = Depends(get_db)):
    row = db.query(Perfil).filter(Perfil.usuario_id == usuario_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return build_success_response(data=PerfilOut.model_validate(row).model_dump(mode="json"), message="Perfil actualizado")


@router.get("/busqueda/avanzada")
def advanced_search(
    nombre: str | None = Query(default=None),
    documento: str | None = Query(default=None),
    email: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    ciudad: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Usuario, Perfil).outerjoin(Perfil, Perfil.usuario_id == Usuario.id)
    if nombre:
        like = f"%{nombre}%"
        query = query.filter(or_(Perfil.primer_nombre.ilike(like), Perfil.primer_apellido.ilike(like), Usuario.username.ilike(like)))
    if documento:
        query = query.filter(Perfil.numero_documento == documento)
    if email:
        query = query.filter(Usuario.email.ilike(f"%{email}%"))
    if estado:
        query = query.filter(Usuario.estado == estado)
    if ciudad:
        query = query.filter(Perfil.ciudad.ilike(f"%{ciudad}%"))

    total = query.count()
    pages = math.ceil(total / size) if total else 1
    rows = query.order_by(Usuario.id.desc()).offset((page - 1) * size).limit(size).all()
    items = []
    for user, profile in rows:
        item = _user_to_out(user)
        item["perfil"] = PerfilOut.model_validate(profile).model_dump(mode="json") if profile else None
        items.append(item)
    return build_success_response(
        data={"items": items, "page": page, "size": size, "total": total, "total_pages": pages},
        message="Busqueda avanzada ejecutada",
    )


@router.get("/buscar/email/{email}")
def find_by_email(email: str, db: Session = Depends(get_db)):
    row = db.query(Usuario).filter(Usuario.email == email).first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return build_success_response(data=_user_to_out(row), message="Usuario encontrado por email")


@router.get("/buscar/documento/{numero_documento}")
def find_by_document(numero_documento: str, db: Session = Depends(get_db)):
    profile = db.query(Perfil).filter(Perfil.numero_documento == numero_documento).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user = db.query(Usuario).filter(Usuario.id == profile.usuario_id).first()
    return build_success_response(data=_user_to_out(user), message="Usuario encontrado por documento")


@router.get("/internal/username/{username}")
def internal_by_username(username: str, db: Session = Depends(get_db)):
    row = db.query(Usuario).filter(Usuario.username == username).first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return build_success_response(
        data={"id": row.id, "username": row.username, "email": row.email, "password_hash": row.password_hash, "estado": row.estado},
        message="Usuario interno",
    )


@router.get("/internal/email/{email}")
def internal_by_email(email: str, db: Session = Depends(get_db)):
    row = db.query(Usuario).filter(Usuario.email == email).first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return build_success_response(
        data={"id": row.id, "username": row.username, "email": row.email, "password_hash": row.password_hash, "estado": row.estado},
        message="Usuario interno",
    )
