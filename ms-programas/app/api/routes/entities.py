from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.responses import build_success_response
from app.db.session import get_db
from app.models.entities import Asignatura, MallaVersion, Programa, Prerrequisito
from app.schemas.entities import AsignaturaIn, MallaVersionIn, ProgramaIn, PrerrequisitoIn

router = APIRouter(tags=["ms-programas"])


def _has_cycle(db: Session, asignatura_id: int, prerrequisito_id: int) -> bool:
    graph = defaultdict(list)
    rows = db.query(Prerrequisito).all()
    for row in rows:
        graph[row.asignatura_id].append(row.prerrequisito_id)
    graph[asignatura_id].append(prerrequisito_id)

    def dfs(node: int, target: int, visited: set[int]) -> bool:
        if node == target:
            return True
        if node in visited:
            return False
        visited.add(node)
        for nxt in graph.get(node, []):
            if dfs(nxt, target, visited):
                return True
        return False

    return dfs(prerrequisito_id, asignatura_id, set())


@router.post("/programas")
def create_program(payload: ProgramaIn, db: Session = Depends(get_db)):
    if db.query(Programa).filter(Programa.codigo == payload.codigo).first():
        raise HTTPException(status_code=409, detail="Codigo de programa duplicado")
    row = Programa(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id}, message="Programa creado")


@router.get("/programas")
def list_programs(db: Session = Depends(get_db)):
    rows = db.query(Programa).order_by(Programa.id.desc()).all()
    data = [
        {
            "id": x.id,
            "codigo": x.codigo,
            "nombre": x.nombre,
            "descripcion": x.descripcion,
            "duracion_semestres": x.duracion_semestres,
            "total_creditos_requeridos": x.total_creditos_requeridos,
            "estado": x.estado,
            "coordinador_usuario_id": x.coordinador_usuario_id,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Programas listados")


@router.put("/programas/{programa_id}")
def update_program(programa_id: int, payload: ProgramaIn, db: Session = Depends(get_db)):
    row = db.query(Programa).filter(Programa.id == programa_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    return build_success_response(data={"id": programa_id}, message="Programa actualizado")


@router.post("/programas/{programa_id}/desactivar")
def deactivate_program(programa_id: int, db: Session = Depends(get_db)):
    row = db.query(Programa).filter(Programa.id == programa_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    row.estado = "inactivo"
    db.commit()
    return build_success_response(data={"id": programa_id}, message="Programa desactivado")


@router.post("/asignaturas")
def create_subject(payload: AsignaturaIn, db: Session = Depends(get_db)):
    if not db.query(Programa).filter(Programa.id == payload.programa_id).first():
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    if db.query(Asignatura).filter(Asignatura.codigo == payload.codigo).first():
        raise HTTPException(status_code=409, detail="Codigo de asignatura duplicado")
    row = Asignatura(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id}, message="Asignatura creada")


@router.get("/asignaturas")
def list_subjects(programa_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Asignatura)
    if programa_id:
        query = query.filter(Asignatura.programa_id == programa_id)
    rows = query.order_by(Asignatura.semestre_sugerido.asc(), Asignatura.nombre.asc()).all()
    data = [
        {
            "id": x.id,
            "codigo": x.codigo,
            "nombre": x.nombre,
            "descripcion": x.descripcion,
            "creditos": x.creditos,
            "semestre_sugerido": x.semestre_sugerido,
            "programa_id": x.programa_id,
            "horas_semanales": x.horas_semanales,
            "tipo": x.tipo,
            "estado": x.estado,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Asignaturas listadas")


@router.put("/asignaturas/{asignatura_id}")
def update_subject(asignatura_id: int, payload: AsignaturaIn, db: Session = Depends(get_db)):
    row = db.query(Asignatura).filter(Asignatura.id == asignatura_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    return build_success_response(data={"id": asignatura_id}, message="Asignatura actualizada")


@router.post("/prerrequisitos")
def create_prereq(payload: PrerrequisitoIn, db: Session = Depends(get_db)):
    if payload.asignatura_id == payload.prerrequisito_id:
        raise HTTPException(status_code=400, detail="Una asignatura no puede ser prerrequisito de si misma")
    if not db.query(Asignatura).filter(Asignatura.id == payload.asignatura_id).first():
        raise HTTPException(status_code=404, detail="Asignatura objetivo no encontrada")
    if not db.query(Asignatura).filter(Asignatura.id == payload.prerrequisito_id).first():
        raise HTTPException(status_code=404, detail="Asignatura prerrequisito no encontrada")
    if _has_cycle(db, payload.asignatura_id, payload.prerrequisito_id):
        raise HTTPException(status_code=409, detail="No se permite crear ciclos en prerrequisitos")
    if db.query(Prerrequisito).filter(
        Prerrequisito.asignatura_id == payload.asignatura_id,
        Prerrequisito.prerrequisito_id == payload.prerrequisito_id,
    ).first():
        raise HTTPException(status_code=409, detail="Prerrequisito duplicado")
    row = Prerrequisito(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id}, message="Prerrequisito asignado")


@router.delete("/prerrequisitos")
def remove_prereq(asignatura_id: int, prerrequisito_id: int, db: Session = Depends(get_db)):
    row = db.query(Prerrequisito).filter(
        Prerrequisito.asignatura_id == asignatura_id,
        Prerrequisito.prerrequisito_id == prerrequisito_id,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Prerrequisito no encontrado")
    db.delete(row)
    db.commit()
    return build_success_response(data={"asignatura_id": asignatura_id, "prerrequisito_id": prerrequisito_id}, message="Prerrequisito removido")


@router.get("/malla/{programa_id}")
def curriculum(programa_id: int, db: Session = Depends(get_db)):
    if not db.query(Programa).filter(Programa.id == programa_id).first():
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    asignaturas = db.query(Asignatura).filter(Asignatura.programa_id == programa_id).all()
    prereqs = db.query(Prerrequisito).all()
    pre_map = defaultdict(list)
    for p in prereqs:
        pre_map[p.asignatura_id].append({"prerrequisito_id": p.prerrequisito_id, "tipo": p.tipo})
    grouped = defaultdict(list)
    for a in asignaturas:
        grouped[a.semestre_sugerido].append(
            {
                "id": a.id,
                "codigo": a.codigo,
                "nombre": a.nombre,
                "creditos": a.creditos,
                "horas_semanales": a.horas_semanales,
                "tipo": a.tipo,
                "prerrequisitos": pre_map.get(a.id, []),
            }
        )
    return build_success_response(data=dict(grouped), message="Malla curricular")


@router.post("/mallas-version")
def create_version(payload: MallaVersionIn, db: Session = Depends(get_db)):
    if payload.estado == "vigente":
        db.query(MallaVersion).filter(MallaVersion.programa_id == payload.programa_id, MallaVersion.estado == "vigente").update({"estado": "historica"})
    row = MallaVersion(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id}, message="Version de malla creada")


@router.get("/mallas-version/{programa_id}")
def list_versions(programa_id: int, db: Session = Depends(get_db)):
    rows = db.query(MallaVersion).filter(MallaVersion.programa_id == programa_id).order_by(MallaVersion.created_at.desc()).all()
    data = [
        {
            "id": x.id,
            "programa_id": x.programa_id,
            "version_identificador": x.version_identificador,
            "fecha_vigencia_inicio": x.fecha_vigencia_inicio.isoformat() if x.fecha_vigencia_inicio else None,
            "fecha_vigencia_fin": x.fecha_vigencia_fin.isoformat() if x.fecha_vigencia_fin else None,
            "estado": x.estado,
            "descripcion_cambios": x.descripcion_cambios,
            "creado_por": x.creado_por,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Versiones de malla")


@router.get("/internal/asignaturas/{asignatura_id}")
def internal_subject(asignatura_id: int, db: Session = Depends(get_db)):
    row = db.query(Asignatura).filter(Asignatura.id == asignatura_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return build_success_response(
        data={
            "id": row.id,
            "codigo": row.codigo,
            "nombre": row.nombre,
            "creditos": row.creditos,
            "programa_id": row.programa_id,
        },
        message="Asignatura interna",
    )


@router.get("/internal/asignaturas/{asignatura_id}/prerrequisitos")
def internal_prereqs(asignatura_id: int, db: Session = Depends(get_db)):
    rows = db.query(Prerrequisito).filter(Prerrequisito.asignatura_id == asignatura_id).all()
    data = [{"prerrequisito_id": x.prerrequisito_id, "tipo": x.tipo} for x in rows]
    return build_success_response(data=data, message="Prerrequisitos de asignatura")
