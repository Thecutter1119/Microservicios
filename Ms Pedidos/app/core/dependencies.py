from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
import httpx
import logging

from app.core.config import settings
from app.clients.http_clients import AuthClient, RolClient

logger = logging.getLogger(__name__)

async def verify_user_session_and_permission(request: Request, required_permission: str):
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    
    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de sesión o el formato no es Bearer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if settings.SECURITY_MOCK_ENABLED:
        return {"usuario_id": 1, "rol": "Administrador", "token": token, "mock": True}
        
    user_data = await AuthClient.validar_sesion(token)
    
    rol = user_data.get("rol")
    if not rol:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario sin rol asignado")
        
    await RolClient.verificar_permiso(rol, required_permission)
    
    return user_data

async def verify_app_token(request: Request):
    import hmac
    
    app_token = request.headers.get("X-App-Token")
    
    if not app_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-App-Token faltante")
        
    if not hmac.compare_digest(app_token.encode(), settings.DOM_APP_TOKEN.encode()):
        logger.warning(f"Intento de acceso S2S con token inválido: {app_token[:5]}...")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de aplicación inválido")
        
    return {"service": "ms-domicilios", "is_service": True}
