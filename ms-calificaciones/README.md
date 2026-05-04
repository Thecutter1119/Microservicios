# ms-calificaciones

Microservicio base del ERP Universitario (CAL) implementado con FastAPI + PostgreSQL.

## Ejecutar

1. `pip install -r requirements.txt`
2. Copiar `.env.example` a `.env`.
3. Crear la base con `init_postgres.sql`.
4. `uvicorn app.main:app --reload --port 80`

## Endpoints Base

- `GET /health`
- `GET /api/v1/calificaciones`
- `POST /api/v1/calificaciones`
- `GET /api/v1/calificaciones/{id}`
