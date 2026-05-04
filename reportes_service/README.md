# ms-reportes [REP]

> **Módulo 6 — Transversales | FastAPI + Python + PostgreSQL | Marzo 2026**

Microservicio de generación consolidada de reportes institucionales. Orquesta datos de múltiples microservicios fuente, gestiona plantillas de reporte, programaciones automáticas y un sistema de caché para evitar regeneraciones innecesarias.

---

## Estructura del Proyecto

```
reportes_service/
│
├── app/
│   ├── main.py                        ← Punto de entrada FastAPI + lifespan + firma
│   │
│   ├── core/
│   │   ├── config.py                  ← Settings (env vars, URLs, timeouts)
│   │   └── security.py                ← REP-RF-003: Request ID, headers salientes
│   │
│   ├── db/
│   │   ├── database.py                ← Engine async + get_db dependency
│   │   └── base.py                    ← DeclarativeBase SQLAlchemy
│   │
│   ├── models/
│   │   ├── plantilla.py               ← ORM: rep_plantillas
│   │   ├── reporte.py                 ← ORM: rep_reportes
│   │   └── programacion.py            ← ORM: rep_programaciones
│   │
│   ├── schemas/
│   │   ├── plantilla_schema.py        ← Pydantic: PlantillaCreate/Update/Out
│   │   ├── reporte_schema.py          ← Pydantic: ReporteCreate/Out
│   │   └── programacion_schema.py     ← Pydantic: ProgramacionCreate/Update/Out
│   │
│   ├── services/
│   │   ├── microservice_client.py     ← REP-RF-001/002: AUT + ROL; REP-RF-012: fuentes
│   │   ├── plantilla_service.py       ← REP-RF-006 a REP-RF-010
│   │   ├── reporte_service.py         ← REP-RF-011 a REP-RF-014, RF-021, RF-022
│   │   ├── programacion_service.py    ← REP-RF-015 a REP-RF-020, RF-023, RF-024
│   │   └── scheduler_service.py       ← REP-RF-019: APScheduler
│   │
│   ├── routers/
│   │   ├── plantilla_router.py        ← 5 endpoints de plantillas
│   │   ├── reporte_router.py          ← 5 endpoints de reportes
│   │   └── programacion_router.py     ← 7 endpoints de programaciones
│   │
│   └── utils/
│       ├── csv_generator.py           ← Generador CSV/JSON + Content-Disposition
│       ├── cache_manager.py           ← Clave de caché determinística
│       └── logger_async.py            ← REP-RF-004: Auditoría fire-and-forget
│
├── index.html                         ← Frontend completo conectado a la API
├── requirements.txt
└── README.md
```

---

## Requisitos Funcionales Implementados

| Categoría | IDs | Cobertura |
|---|---|---|
| Transversales | REP-RF-001 a 005 | ✅ Completa |
| Plantillas | REP-RF-006 a 010 | ✅ Completa |
| Reportes | REP-RF-011 a 014 | ✅ Completa |
| Programaciones | REP-RF-015 a 020 | ✅ Completa |
| Sugeridos | REP-RF-021 a 024 | ✅ Completa |
| **TOTAL** | **24 requisitos** | **100%** |

---

## Endpoints Expuestos (16 endpoints HTTP)

### Plantillas de Reporte
| Método | Endpoint | RF |
|---|---|---|
| `POST` | `/api/v1/plantillas` | REP-RF-006 |
| `GET` | `/api/v1/plantillas` | REP-RF-008 |
| `GET` | `/api/v1/plantillas/{id}` | REP-RF-007 |
| `PUT` | `/api/v1/plantillas/{id}` | REP-RF-009 |
| `DELETE` | `/api/v1/plantillas/{id}` | REP-RF-010 |

### Reportes
| Método | Endpoint | RF |
|---|---|---|
| `POST` | `/api/v1/reportes` | REP-RF-011 |
| `GET` | `/api/v1/reportes` | REP-RF-021 |
| `GET` | `/api/v1/reportes/{id}` | REP-RF-013 |
| `GET` | `/api/v1/reportes/{id}/descargar` | REP-RF-014 |
| `POST` | `/api/v1/reportes/{id}/invalidar-cache` | REP-RF-022 |

### Programaciones
| Método | Endpoint | RF |
|---|---|---|
| `POST` | `/api/v1/programaciones` | REP-RF-015 |
| `GET` | `/api/v1/programaciones` | REP-RF-016 |
| `GET` | `/api/v1/programaciones/{id}` | REP-RF-024 |
| `PUT` | `/api/v1/programaciones/{id}` | REP-RF-017 |
| `POST` | `/api/v1/programaciones/{id}/desactivar` | REP-RF-018 |
| `POST` | `/api/v1/programaciones/{id}/reactivar` | REP-RF-023 |
| `POST` | `/api/v1/programaciones/{id}/ejecutar` | REP-RF-020 |

### Sistema
| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Firma del microservicio |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

---

## Instalación y Arranque

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (opcional — tiene defaults)
cp .env.example .env

# 4. Levantar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor crea las tablas automáticamente en arranque (modo dev).  
En producción usar **Alembic** para migraciones.

---

## Variables de Entorno

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://rep_user:rep_pass@localhost:5432/db_reportes` | URL async |
| `APP_TOKEN_REP` | `REP-APP-TOKEN-SECRET-2026` | Token del servicio |
| `MS_AUTENTICACION_URL` | `http://autenticacion-svc:8000` | — |
| `MS_ROLES_URL` | `http://roles-svc:8005` | — |
| `MS_CALIFICACIONES_URL` | `http://calificaciones-svc:8001` | — |
| `MS_INVENTARIO_URL` | `http://inventario-svc:8002` | — |
| `MS_PRESUPUESTO_URL` | `http://presupuesto-svc:8003` | — |
| `MS_AUDITORIA_URL` | `http://auditoria-svc:8004` | — |
| `TIMEOUT_AUTH` | `3` | Timeout AUT/ROL (seg) |
| `TIMEOUT_SOURCES` | `30` | Timeout fuentes (seg) |
| `TIMEOUT_AUDIT` | `2` | Timeout AUD fire-and-forget |
| `SCHEDULER_INTERVAL_MINUTES` | `1` | Frecuencia del scheduler |

---

## Respuesta Estándar (REP-RF-005)

```json
{
  "request_id": "REP-1740000000-a3f8b2",
  "success": true,
  "data": { ... },
  "message": "Operación exitosa",
  "timestamp": "2026-03-15T12:00:00Z"
}
```

El `request_id` también viaja en el header `X-Request-ID` de cada respuesta.

---

## Integraciones

```
ms-reportes [REP]
  ├── ms-autenticacion [AUT]  ← POST /sesiones/validar        (síncrono, timeout 3s)
  ├── ms-roles         [ROL]  ← POST /permisos/verificar      (síncrono, timeout 3s)
  ├── ms-calificaciones [CAL] ← GET  /reportes/rendimiento    (async interno, timeout 30s)
  ├── ms-inventario    [INV]  ← GET  /reportes/activos        (async interno, timeout 30s)
  ├── ms-presupuesto   [PRE]  ← GET  /reportes/ejecucion      (async interno, timeout 30s)
  └── ms-auditoria     [AUD]  ← POST /api/v1/logs             (fire-and-forget, timeout 2s)
```

---

*ms-reportes [REP] — Módulo 6 Transversales — v1.0.0 — Marzo 2026*
