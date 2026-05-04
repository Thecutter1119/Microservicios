import secrets
import time

from fastapi import Request, Response


def _new_request_id() -> str:
    return f"DOM-{int(time.time())}-{secrets.token_hex(3)}"


async def request_id_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("X-Request-ID") or _new_request_id()
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
