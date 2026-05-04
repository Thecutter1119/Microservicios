import time
import secrets
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        
        if not request_id:
            timestamp = int(time.time())
            short_id = secrets.token_hex(3)
            request_id = f"PED-{timestamp}-{short_id}"
            
        token = request_id_ctx.set(request_id)
        
        response = await call_next(request)
        
        response.headers["X-Request-ID"] = request_id
        
        request_id_ctx.reset(token)
        
        return response

def get_current_request_id() -> str:
    return request_id_ctx.get()
