# ERP Universitario - Microservicios

Repositorio del ERP universitario basado en 19 microservicios con FastAPI + PostgreSQL.

## Opcion 1: Ejecutar Con Docker (Recomendada)

### Requisitos
- Docker Desktop instalado y corriendo.
- Docker Compose habilitado (`docker compose version`).
- Puertos libres `8101` a `8119`.

### Levantar Todo
Desde la raiz del proyecto (`c:\Users\jhons\Downloads\Microservicios`):

```bash
docker compose up -d --build
```

Esto levanta:
- 19 microservicios
- 19 bases de datos PostgreSQL (una por microservicio)
- Red Docker `erp-net`

### Verificar
```bash
docker compose ps
```

Todos deben aparecer en estado `Up`.

Prueba rapida:

```powershell
.\smoke_test.ps1
```

### Logs
```bash
docker compose logs -f ms-autenticacion
docker compose logs --tail=100 ms-roles
```

### Detener
```bash
docker compose down
```

Detener y borrar datos (volumenes):

```bash
docker compose down -v
```

## Opcion 2: Ejecutar Local (Sin Docker)

### Requisitos
- Python 3.11+ instalado.
- `pip` disponible.
- PostgreSQL accesible para cada microservicio (segun sus `.env` / `.env.example`).
- Puertos libres `8101` a `8119`.

### Instalar Dependencias Y Levantar
Desde la raiz:

```powershell
.\run_all.ps1 -InstallDeps
```

Si ya instalaste dependencias antes:

```powershell
.\run_all.ps1
```

Notas:
- `run_all.ps1` ejecuta los microservicios en modo local.
- Si falta configuracion de DB en algun `.env`, el servicio puede iniciar y caer por conexion.

### Verificar
```powershell
.\smoke_test.ps1
```

### Detener
```powershell
.\stop_all.ps1
```

## Probar En Postman
Coleccion lista:

- `postman/ERP_Universitario_Funcional_Completo_.json`

Pasos:
1. Importar el archivo en Postman.
2. Ejecutar la carpeta de flujo integrado (`Auth -> ...`) o carpetas individuales.
3. Validar respuestas `2xx/4xx controlado` y ausencia de `500`.

## Endpoints De Salud (Ejemplos)
- `http://localhost:8101/health` (`ms-autenticacion`)
- `http://localhost:8102/health` (`ms-roles`)
- `http://localhost:8103/health` (`ms-usuarios`)
- `http://localhost:8119/health` (`ms-reportes`)
