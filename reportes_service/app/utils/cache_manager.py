"""
ms-reportes [REP] — Gestión de caché de reportes
REP-RF-011: Lógica de detección de caché existente
REP-RF-022: Invalidación de caché
"""

import hashlib
import json


def build_cache_key(plantilla_id: int, parametros: dict, formato_salida: str) -> str:
    """
    Genera una clave determinística para buscar reportes en caché.
    Misma plantilla + mismos parámetros (ordenados) + mismo formato = misma clave.
    """
    normalized = {
        "plantilla_id": plantilla_id,
        "parametros": dict(sorted(parametros.items())),
        "formato": formato_salida.upper(),
    }
    payload = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def serialize_params(parametros: dict) -> str:
    """Serializa parámetros para comparación en base de datos."""
    return json.dumps(dict(sorted(parametros.items())), sort_keys=True, ensure_ascii=False)
