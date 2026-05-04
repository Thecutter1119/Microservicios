import secrets
import time
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = f"{settings.SERVICE_CODE}-{int(time.time())}-{secrets.token_hex(3)}"

        token = request_id_ctx.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        request_id_ctx.reset(token)
        return response


def get_current_request_id() -> str:
    return request_id_ctx.get()
