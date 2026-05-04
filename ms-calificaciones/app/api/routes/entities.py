from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.responses import build_success_response
from app.db.session import get_db
from app.models.entities import CorteEvaluativo, Nota, PromedioEstudiante
from app.schemas.entities import CorteIn, NotaIn

router = APIRouter(tags=["ms-calificaciones"])


def _definitiva(db: Session, inscripcion_id: int) -> float:
    rows = db.query(Nota, CorteEvaluativo).join(CorteEvaluativo, CorteEvaluativo.id == Nota.corte_id).filter(
        Nota.inscripcion_id == inscripcion_id
    ).all()
    total = 0.0
    for nota, corte in rows:
        total += float(nota.nota) * (float(corte.porcentaje) / 100)
    return round(total, 2)


@router.post("/cortes")
def create_cut(payload: CorteIn, db: Session = Depends(get_db)):
    current = db.query(func.coalesce(func.sum(CorteEvaluativo.porcentaje), 0)).filter(
        CorteEvaluativo.asignatura_id == payload.asignatura_id,
        CorteEvaluativo.periodo_id == payload.periodo_id,
    ).scalar()
    if float(current) + payload.porcentaje > 100:
        raise HTTPException(status_code=409, detail="La suma de porcentajes de cortes no puede superar 100")
    row = CorteEvaluativo(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id}, message="Corte creado")


@router.get("/cortes")
def list_cuts(db: Session = Depends(get_db)):
    rows = db.query(CorteEvaluativo).order_by(CorteEvaluativo.id.desc()).all()
    data = [
        {
            "id": x.id,
            "asignatura_id": x.asignatura_id,
            "periodo_id": x.periodo_id,
            "nombre": x.nombre,
            "porcentaje": float(x.porcentaje),
            "numero_corte": x.numero_corte,
            "fecha_inicio": x.fecha_inicio.isoformat() if x.fecha_inicio else None,
            "fecha_fin": x.fecha_fin.isoformat() if x.fecha_fin else None,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Cortes listados")


@router.post("/notas")
def create_note(payload: NotaIn, db: Session = Depends(get_db)):
    if payload.nota < 0 or payload.nota > 5:
        raise HTTPException(status_code=400, detail="La nota debe estar entre 0.0 y 5.0")
    row = Nota(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return build_success_response(data={"id": row.id}, message="Nota registrada")


@router.put("/notas/{nota_id}")
def update_note(nota_id: int, payload: NotaIn, db: Session = Depends(get_db)):
    row = db.query(Nota).filter(Nota.id == nota_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    row.inscripcion_id = payload.inscripcion_id
    row.corte_id = payload.corte_id
    row.nota = payload.nota
    row.observaciones = payload.observaciones
    row.registrado_por = payload.registrado_por
    db.commit()
    return build_success_response(data={"id": nota_id}, message="Nota actualizada")


@router.get("/inscripciones/{inscripcion_id}/notas")
def notes_by_inscription(inscripcion_id: int, db: Session = Depends(get_db)):
    rows = db.query(Nota).filter(Nota.inscripcion_id == inscripcion_id).all()
    data = [
        {
            "id": x.id,
            "corte_id": x.corte_id,
            "nota": float(x.nota),
            "observaciones": x.observaciones,
            "registrado_por": x.registrado_por,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Notas por inscripcion")


@router.get("/cortes/{corte_id}/notas")
def notes_by_cut(corte_id: int, db: Session = Depends(get_db)):
    rows = db.query(Nota).filter(Nota.corte_id == corte_id).all()
    data = [
        {
            "id": x.id,
            "inscripcion_id": x.inscripcion_id,
            "nota": float(x.nota),
            "observaciones": x.observaciones,
            "registrado_por": x.registrado_por,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Notas por corte")


@router.get("/inscripciones/{inscripcion_id}/definitiva")
def final_grade(inscripcion_id: int, db: Session = Depends(get_db)):
    definitiva = _definitiva(db, inscripcion_id)
    estado = "aprobada" if definitiva >= 3.0 else "reprobada"
    return build_success_response(data={"inscripcion_id": inscripcion_id, "definitiva": definitiva, "estado": estado}, message="Nota definitiva calculada")


@router.post("/promedios/recalcular")
def recompute_average(estudiante_id: int, periodo_id: int, creditos_cursados: int, creditos_aprobados: int, db: Session = Depends(get_db)):
    # Simplificado: promedio periodo desde notas del estudiante (no pondera por creditos por no dependencia directa a programas).
    # El endpoint recibe creditos cursados/aprobados para mantener trazabilidad de la metrica.
    notas = db.query(Nota).all()
    valores = [float(x.nota) for x in notas]
    promedio_periodo = round(sum(valores) / len(valores), 2) if valores else 0.0
    previos = db.query(PromedioEstudiante).filter(PromedioEstudiante.estudiante_id == estudiante_id).all()
    total_prom = promedio_periodo + sum(float(x.promedio_periodo) for x in previos)
    promedio_acumulado = round(total_prom / (len(previos) + 1), 2)
    row = PromedioEstudiante(
        estudiante_id=estudiante_id,
        periodo_id=periodo_id,
        promedio_periodo=promedio_periodo,
        promedio_acumulado=promedio_acumulado,
        creditos_cursados=creditos_cursados,
        creditos_aprobados=creditos_aprobados,
    )
    db.add(row)
    db.commit()
    return build_success_response(data={"id": row.id, "promedio_periodo": promedio_periodo, "promedio_acumulado": promedio_acumulado}, message="Promedio recalculado")


@router.get("/promedios/estudiante/{estudiante_id}")
def student_averages(estudiante_id: int, db: Session = Depends(get_db)):
    rows = db.query(PromedioEstudiante).filter(PromedioEstudiante.estudiante_id == estudiante_id).order_by(PromedioEstudiante.id.desc()).all()
    data = [
        {
            "id": x.id,
            "periodo_id": x.periodo_id,
            "promedio_periodo": float(x.promedio_periodo),
            "promedio_acumulado": float(x.promedio_acumulado),
            "creditos_aprobados": x.creditos_aprobados,
            "creditos_cursados": x.creditos_cursados,
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Promedios del estudiante")


@router.get("/promedios/bajo-rendimiento")
def low_performance(umbral: float = 3.0, db: Session = Depends(get_db)):
    rows = db.query(PromedioEstudiante).filter(PromedioEstudiante.promedio_periodo < umbral).all()
    data = [
        {
            "estudiante_id": x.estudiante_id,
            "periodo_id": x.periodo_id,
            "promedio_periodo": float(x.promedio_periodo),
            "promedio_acumulado": float(x.promedio_acumulado),
        }
        for x in rows
    ]
    return build_success_response(data=data, message="Estudiantes con bajo rendimiento")
