from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.responses import build_success_response
from app.db.session import get_db
from app.models.entities import Permiso, Rol, RolPermiso, UsuarioRol
from app.schemas.entities import AssignPermisosIn, AssignRolUsuarioIn, PermisoIn, PermisoOut, RemoveRolUsuarioIn, RolIn, RolOut

router = APIRouter(tags=["ms-roles"])


def _contradictory_pairs() -> set[tuple[str, str]]:
    pairs = set()
    for raw in settings.CONTRADICTORY_ROLE_PAIRS.split("|"):
        if ":" in raw:
            left, right = raw.split(":", maxsplit=1)
            pairs.add((left.strip().lower(), right.strip().lower()))
            pairs.add((right.strip().lower(), left.strip().lower()))
    return pairs


@router.post("/roles")
def create_role(payload: RolIn, db: Session = Depends(get_db)):
    if db.query(Rol).filter(Rol.nombre.ilike(payload.nombre)).first():
        raise HTTPException(status_code=409, detail="El rol ya existe")
    row = Rol(nombre=payload.nombre, descripcion=payload.descripcion)
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data=RolOut.model_validate(row).model_dump(mode="json"), message="Rol creado")


@router.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    rows = db.query(Rol).order_by(Rol.nombre.asc()).all()
    data = [RolOut.model_validate(x).model_dump(mode="json") for x in rows]
    return build_success_response(data=data, message="Roles listados")


@router.put("/roles/{rol_id}")
def update_role(rol_id: int, payload: RolIn, db: Session = Depends(get_db)):
    row = db.query(Rol).filter(Rol.id == rol_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    row.nombre = payload.nombre
    row.descripcion = payload.descripcion
    db.commit()
    db.refresh(row)
    return build_success_response(data=RolOut.model_validate(row).model_dump(mode="json"), message="Rol actualizado")


@router.post("/roles/{rol_id}/desactivar")
def deactivate_role(rol_id: int, db: Session = Depends(get_db)):
    row = db.query(Rol).filter(Rol.id == rol_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    row.estado = "inactivo"
    db.commit()
    return build_success_response(data={"rol_id": rol_id}, message="Rol desactivado")


@router.post("/permisos")
def create_permission(payload: PermisoIn, db: Session = Depends(get_db)):
    if db.query(Permiso).filter(Permiso.codigo == payload.codigo).first():
        raise HTTPException(status_code=409, detail="El codigo de permiso ya existe")
    row = Permiso(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data=PermisoOut.model_validate(row).model_dump(mode="json"), message="Permiso creado")


@router.get("/permisos")
def list_permissions(db: Session = Depends(get_db)):
    rows = db.query(Permiso).order_by(Permiso.modulo.asc(), Permiso.codigo.asc()).all()
    data = [PermisoOut.model_validate(x).model_dump(mode="json") for x in rows]
    return build_success_response(data=data, message="Permisos listados")


@router.put("/permisos/{permiso_id}")
def update_permission(permiso_id: int, payload: PermisoIn, db: Session = Depends(get_db)):
    row = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return build_success_response(data=PermisoOut.model_validate(row).model_dump(mode="json"), message="Permiso actualizado")


@router.delete("/permisos/{permiso_id}")
def delete_permission(permiso_id: int, db: Session = Depends(get_db)):
    row = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    db.query(RolPermiso).filter(RolPermiso.permiso_id == permiso_id).delete()
    db.delete(row)
    db.commit()
    return build_success_response(data={"permiso_id": permiso_id}, message="Permiso eliminado")


@router.post("/roles/{rol_id}/permisos")
def assign_permissions_to_role(rol_id: int, payload: AssignPermisosIn, db: Session = Depends(get_db)):
    role = db.query(Rol).filter(Rol.id == rol_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    for permiso_id in payload.permiso_ids:
        if not db.query(Permiso).filter(Permiso.id == permiso_id).first():
            raise HTTPException(status_code=404, detail=f"Permiso no encontrado: {permiso_id}")
        exists = db.query(RolPermiso).filter(and_(RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso_id)).first()
        if not exists:
            db.add(RolPermiso(rol_id=rol_id, permiso_id=permiso_id, assigned_by=payload.assigned_by))
    db.commit()
    return build_success_response(data={"rol_id": rol_id, "permiso_ids": payload.permiso_ids}, message="Permisos asignados")


@router.delete("/roles/{rol_id}/permisos/{permiso_id}")
def remove_permission_from_role(rol_id: int, permiso_id: int, db: Session = Depends(get_db)):
    row = db.query(RolPermiso).filter(and_(RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso_id)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Asignacion no encontrada")
    db.delete(row)
    db.commit()
    return build_success_response(data={"rol_id": rol_id, "permiso_id": permiso_id}, message="Permiso removido del rol")


@router.post("/usuarios/{usuario_id}/roles")
def assign_role_to_user(usuario_id: int, payload: AssignRolUsuarioIn, db: Session = Depends(get_db)):
    role = db.query(Rol).filter(Rol.id == payload.rol_id, Rol.estado == "activo").first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado o inactivo")
    assigned = db.query(UsuarioRol).join(Rol, Rol.id == UsuarioRol.rol_id).filter(
        UsuarioRol.usuario_id == usuario_id, UsuarioRol.estado == "activo"
    ).all()
    pair_set = _contradictory_pairs()
    for current in assigned:
        current_role = db.query(Rol).filter(Rol.id == current.rol_id).first()
        if current_role and (current_role.nombre.lower(), role.nombre.lower()) in pair_set:
            raise HTTPException(status_code=409, detail="Asignacion de rol contradictoria")
    existing = db.query(UsuarioRol).filter(
        UsuarioRol.usuario_id == usuario_id, UsuarioRol.rol_id == payload.rol_id
    ).first()
    if existing:
        existing.estado = "activo"
        existing.assigned_by = payload.assigned_by
    else:
        db.add(UsuarioRol(usuario_id=usuario_id, rol_id=payload.rol_id, assigned_by=payload.assigned_by, estado="activo"))
    db.commit()
    return build_success_response(data={"usuario_id": usuario_id, "rol_id": payload.rol_id}, message="Rol asignado al usuario")


@router.get("/usuarios/{usuario_id}/roles")
def list_user_roles(usuario_id: int, db: Session = Depends(get_db)):
    rows = db.query(UsuarioRol, Rol).join(Rol, Rol.id == UsuarioRol.rol_id).filter(
        UsuarioRol.usuario_id == usuario_id, UsuarioRol.estado == "activo"
    ).all()
    data = [
        {"rol_id": role.id, "nombre": role.nombre, "estado_asignacion": rel.estado, "assigned_at": rel.assigned_at.isoformat() if rel.assigned_at else None}
        for rel, role in rows
    ]
    return build_success_response(data=data, message="Roles del usuario")


@router.delete("/usuarios/{usuario_id}/roles")
def remove_user_role(usuario_id: int, payload: RemoveRolUsuarioIn, db: Session = Depends(get_db)):
    row = db.query(UsuarioRol).filter(
        UsuarioRol.usuario_id == usuario_id, UsuarioRol.rol_id == payload.rol_id, UsuarioRol.estado == "activo"
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Asignacion de rol no encontrada")
    row.estado = "inactivo"
    db.commit()
    return build_success_response(data={"usuario_id": usuario_id, "rol_id": payload.rol_id}, message="Rol removido del usuario")


@router.get("/validar-permiso")
def validate_permission(rol_id: int = Query(...), codigo_permiso: str = Query(...), db: Session = Depends(get_db)):
    role = db.query(Rol).filter(Rol.id == rol_id, Rol.estado == "activo").first()
    if not role:
        return build_success_response(data={"autorizado": False}, message="Rol no valido")
    permiso = db.query(Permiso).filter(Permiso.codigo == codigo_permiso).first()
    if not permiso:
        return build_success_response(data={"autorizado": False}, message="Permiso no existe")
    has = db.query(RolPermiso).filter(
        RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso.id
    ).first()
    return build_success_response(data={"autorizado": has is not None}, message="Validacion ejecutada")


@router.get("/permisos/por-modulo")
def permissions_by_module(db: Session = Depends(get_db)):
    rows = db.query(Permiso).order_by(Permiso.modulo.asc(), Permiso.codigo.asc()).all()
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.modulo].append(PermisoOut.model_validate(row).model_dump(mode="json"))
    return build_success_response(data=grouped, message="Permisos agrupados por modulo")


@router.get("/internal/usuarios/{usuario_id}/permisos")
def get_permissions_for_user(usuario_id: int, db: Session = Depends(get_db)):
    query_rows = (
        db.query(Permiso.codigo)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .join(UsuarioRol, UsuarioRol.rol_id == RolPermiso.rol_id)
        .filter(UsuarioRol.usuario_id == usuario_id, UsuarioRol.estado == "activo")
        .distinct()
        .all()
    )
    permisos = [x[0] for x in query_rows]
    return build_success_response(data={"usuario_id": usuario_id, "permisos": permisos}, message="Permisos por usuario")
