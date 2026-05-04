# ms-domicilios-app

Base del microservicio DOM usando FastAPI.

## Estructura

```text
ms-domicilios-app/
	app/          # Codigo fuente del microservicio
	tests/        # Pruebas automatizadas
	requirements.txt
	.env.example
```

## Requisitos

- Python 3.11+
- PostgreSQL en ejecucion
- Driver `psycopg` con binarios (instalado via requirements)

## Instalacion

```bash
pip install -r requirements.txt
```

## Configuracion

Copiar `.env.example` a `.env` y ajustar valores.

Conexion sugerida para tu entorno local:

```text
DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/ms_domicilios
```

## Ejecutar

```bash
uvicorn app.main:app --reload --port 8000
```

## Verificacion rapida

- GET `/health`
- El campo `data.database` indica `connected` o `not_connected`.

## Documentacion del proyecto

La documentacion funcional y de analisis se mantiene fuera del runtime del servicio para no mezclarla con el codigo de ejecucion. Consulta los archivos `DOM-*.md` y la carpeta `Documentacion/` en la raiz del workspace.
