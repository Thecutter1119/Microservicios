from fastapi import HTTPException, status
import httpx
from app.core.config import settings
from app.core.middleware import get_current_request_id

def get_http_client():
    return httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS)

def get_service_headers() -> dict:
    return {
        "X-Request-ID": get_current_request_id(),
        "X-App-Token": settings.PED_APP_TOKEN,
        "Content-Type": "application/json"
    }

class AuthClient:
    @staticmethod
    async def validar_sesion(token: str) -> dict:
        headers = get_service_headers()
        headers["Authorization"] = f"Bearer {token}"
        
        try:
            async with get_http_client() as client:
                response = await client.post(
                    f"{settings.AUTH_BASE_URL}/auth/sesiones/validar",
                    headers=headers,
                    json={"token": token}
                )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                if not data.get("sesion_valida"):
                    raise HTTPException(status_code=401, detail="Sesión no válida o expirada")
                return data
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Sesión no válida o expirada")
            else:
                raise HTTPException(status_code=503, detail="Error en validación de sesión (AUTH)")
                
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de autenticación no disponible")

class RolClient:
    @staticmethod
    async def verificar_permiso(rol: str, codigo_permiso: str) -> bool:
        try:
            async with get_http_client() as client:
                response = await client.post(
                    f"{settings.ROL_BASE_URL}/roles/permisos/verificar",
                    headers=get_service_headers(),
                    json={
                        "rol": rol,
                        "codigo_permiso": codigo_permiso
                    }
                )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                if not data.get("autorizado"):
                    raise HTTPException(status_code=403, detail="Permisos insuficientes")
                return True
            else:
                raise HTTPException(status_code=503, detail="Error en validación de permisos (ROL)")
                
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de roles no disponible")

class ProveedorClient:
    @staticmethod
    async def validar_contrato_vigente(proveedor_id: int) -> dict:
        if settings.EXTERNAL_SERVICES_MOCK_ENABLED:
            return {"proveedor_id": proveedor_id, "contrato_vigente": True, "mock": True}
        try:
            async with get_http_client() as client:
                response = await client.get(
                    f"{settings.PRV_BASE_URL}/api/v1/proveedores/{proveedor_id}/contrato/vigente",
                    headers=get_service_headers()
                )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                if not data.get("contrato_vigente"):
                    raise HTTPException(status_code=422, detail="El proveedor no tiene contrato vigente")
                return data
            elif response.status_code == 422 or response.status_code == 404:
                raise HTTPException(status_code=422, detail="El proveedor no existe o no tiene contrato vigente")
            else:
                raise HTTPException(status_code=503, detail="Error al validar proveedor (PRV)")
                
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de proveedores no disponible")

class InventarioClient:
    @staticmethod
    async def verificar_existencia(activo_id: int) -> bool:
        if settings.EXTERNAL_SERVICES_MOCK_ENABLED:
            return True
        try:
            async with get_http_client() as client:
                response = await client.get(
                    f"{settings.INV_BASE_URL}/activos/{activo_id}",
                    headers=get_service_headers()
                )
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                raise HTTPException(status_code=422, detail=f"Activo {activo_id} no existe en inventario")
            else:
                raise HTTPException(status_code=503, detail="Error al validar activo (INV)")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de inventario no disponible")
            
    @staticmethod
    async def registrar_entrada(activo_id: int, cantidad: float, observaciones: str = "") -> bool:
        if settings.EXTERNAL_SERVICES_MOCK_ENABLED:
            return True
        try:
            async with get_http_client() as client:
                response = await client.post(
                    f"{settings.INV_BASE_URL}/activos/{activo_id}/entradas",
                    headers=get_service_headers(),
                    json={
                        "cantidad": float(cantidad),
                        "motivo": "Recepción de pedido interno",
                        "observaciones": observaciones
                    }
                )
            if response.status_code in (200, 201):
                return True
            else:
                raise HTTPException(status_code=503, detail=f"Fallo al registrar entrada de stock en INV para activo {activo_id}")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de inventario no disponible (recepción abortada)")
