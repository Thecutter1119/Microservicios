from datetime import datetime, timezone

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(FastAPIHTTPException)
    async def http_exception_handler(request: Request, exc: FastAPIHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "DOM-unknown")

        data = None
        message = str(exc.detail)
        if isinstance(exc.detail, dict):
            message = exc.detail.get("message", "Request error")
            data = exc.detail.get("data")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "request_id": request_id,
                "success": False,
                "data": data,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "DOM-unknown")
        fields = sorted({".".join(str(part) for part in err.get("loc", [])[1:]) for err in exc.errors()})
        return JSONResponse(
            status_code=400,
            content={
                "request_id": request_id,
                "success": False,
                "data": {"campos_fallidos": fields},
                "message": "El payload contiene campos obligatorios faltantes o con tipos invalidos.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, _: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "DOM-unknown")
        return JSONResponse(
            status_code=500,
            content={
                "request_id": request_id,
                "success": False,
                "data": None,
                "message": "Internal server error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
