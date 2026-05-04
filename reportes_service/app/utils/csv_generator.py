"""
ms-reportes [REP] — Generador de reportes en formato CSV y JSON
REP-RF-012: Generar Reporte Consolidado
"""

import csv
import io
import json
from typing import Any


def generate_csv(data: list[dict[str, Any]]) -> str:
    """Genera un string CSV a partir de una lista de diccionarios."""
    if not data:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def generate_json(data: Any) -> str:
    """Serializa los datos a JSON compacto para almacenamiento en caché."""
    return json.dumps(data, ensure_ascii=False, default=str)


def format_report(data: Any, formato: str) -> tuple[str, str, str]:
    """
    Formatea los datos consolidados según el formato solicitado.
    Retorna: (contenido_str, content_type, extension)
    """
    fmt = formato.upper()
    if fmt == "CSV":
        rows = data if isinstance(data, list) else [data]
        content = generate_csv(rows)
        return content, "text/csv; charset=utf-8", "csv"
    else:
        content = generate_json(data)
        return content, "application/json", "json"


def build_content_disposition(nombre_reporte: str, extension: str) -> str:
    """Genera el header Content-Disposition para descarga (REP-RF-014)."""
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in nombre_reporte)
    safe_name = safe_name.strip().replace(" ", "_")
    return f'attachment; filename="{safe_name}.{extension}"'
