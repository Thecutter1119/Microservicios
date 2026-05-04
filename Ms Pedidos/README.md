# ms-pedidos (PED)

Microservicio encargado de la gestión de pedidos internos y órdenes de compra de la institución. Construido con FastAPI y PostgreSQL.

## 🛠 Decisiones Técnicas Implementadas
Basado en los documentos de diseño (`.md`), se tomaron las siguientes decisiones para la implementación:

1. **Base de Datos (ORM):** Se utiliza `SQLAlchemy` para interactuar con PostgreSQL de manera segura y orientada a objetos. Esto previene inyecciones SQL y acelera el desarrollo. Las tablas son creadas exactamente como las define el modelo de datos (sin FK foráneas a otros MS).
2. **Auditoría (Asíncrona):** Se implementó mediante `BackgroundTasks` de FastAPI (patrón fire-and-forget). Envía los logs a `ms-auditoria` sin bloquear el response principal y falla silenciosamente si el servicio AUD está caído (Regla RT-05).
3. **Eliminación de ítems (PED-RF-015):** Se implementó como un *Hard Delete* desde la base de datos ya que el modelo original no contemplaba columna `deleted_at`.
4. **Número de pedido:** Se genera automáticamente combinando la fecha y caracteres aleatorios (ej: `PED-20260413-4B9A`).
5. **Autenticación (S2S):** La validación de `X-App-Token` (para que consuma ms-domicilios) se realiza con una función de comparación segura en tiempo constante (`hmac.compare_digest`) para evitar ataques de temporización (timing attacks).
6. **Permisos (Roles):** Se definieron constantes como `"PED_CREAR_PEDIDO"`, `"PED_LISTAR_PEDIDOS"`, etc., como los códigos de permisos requeridos.

## 🚀 Requisitos para Correr en Local

1. Tener Python 3.10+ (probado con Python 3.13)
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Base de Datos: Necesitas una instancia de PostgreSQL corriendo.
   - Crea una BD llamada `db_pedidos`.
4. Configurar variables de entorno. Crea un archivo `.env` en la raíz (puedes usar `.env.example` como base si existiera) o exporta estas variables:
   ```env
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/db_pedidos?sslmode=require
   AUTH_BASE_URL=http://localhost:8001
   ROL_BASE_URL=http://localhost:8002
   PRV_BASE_URL=http://localhost:8003
   INV_BASE_URL=http://localhost:8004
   AUD_BASE_URL=http://localhost:8005
   PED_APP_TOKEN=token-super-secreto-pedidos
   DOM_APP_TOKEN=token-super-secreto-domicilios
   ```

## 🏗 Cómo inicializar y arrancar

1. **Crear tablas en BD:** (Ejecuta esto solo la primera vez para crear las tablas desde SQLAlchemy).
   ```bash
   python -m app.db.init_db
   ```
   Para crear tablas y cargar datos de ejemplo:
   ```bash
   python -m app.db.seed_db
   ```
2. **Levantar el servidor FastAPI:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. **Ver Documentación de la API (Swagger UI):**
   Una vez corriendo, abre en tu navegador:
   👉 `http://localhost:8000/api/v1/docs`

## 📁 Estructura del Código

- `/app/api/routes/pedidos.py`: Contiene los 13 endpoints especificados (Crear, listar, avanzar estado, gestionar ítems, registrar recepción).
- `/app/clients/http_clients.py`: Clientes para conectarse con `ms-autenticacion`, `ms-roles`, `ms-proveedores`, e `ms-inventario`.
- `/app/core/`: Middlewares (generación de Request ID), dependencias (validar sesión y roles), respuestas estandarizadas (incluye auditoría).
- `/app/models/pedidos.py`: Modelos SQLAlchemy para la persistencia de datos.
- `/app/schemas/pedidos.py`: Contratos Pydantic de Request / Response de la API.
