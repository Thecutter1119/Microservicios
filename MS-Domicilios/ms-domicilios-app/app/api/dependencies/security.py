from collections.abc import Callable

from fastapi import HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infrastructure.clients.auth_client import AuthClient
from app.infrastructure.clients.rol_client import RolClient

_auth_client = AuthClient()
_rol_client = RolClient()
bearer_scheme = HTTPBearer(auto_error=False)


def require_permission(permission_code: str) -> Callable:
    async def _dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    ) -> dict[str, str]:
        if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required",
            )

        token = credentials.credentials.strip()

        session = await _auth_client.validate_session(token)
        if not session.is_valid or not session.user_id or not session.role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion invalida o expirada")

        allowed = await _rol_client.has_permission(session.role, permission_code)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

        request.state.user_id = session.user_id
        request.state.role = session.role
        return {"user_id": session.user_id, "role": session.role}

    return _dependency