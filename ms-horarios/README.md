# ms-horarios

Microservicio base del ERP Universitario (HOR) implementado con FastAPI + PostgreSQL.

## Ejecutar

1. `pip install -r requirements.txt`
2. Copiar `.env.example` a `.env`.
3. Crear la base con `init_postgres.sql`.
4. `uvicorn app.main:app --reload --port 80`

## Endpoints Base

- `GET /health`
- `GET /api/v1/franjas`
- `POST /api/v1/franjas`
- `GET /api/v1/franjas/{id}`
