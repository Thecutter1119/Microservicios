from dataclasses import dataclass

import httpx

from app.core.config import get_settings


@dataclass
class PedidoLookupResult:
    exists: bool
    is_eligible: bool
    status_code: int | None = None
    message: str | None = None
    payload: dict | None = None


class PedidosClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    async def lookup_pedido(self, pedido_id: int, request_id: str | None = None) -> PedidoLookupResult:
        if self._settings.ped_mock_enabled:
            return self._lookup_pedido_mock(pedido_id)

        return await self._lookup_pedido_http(pedido_id, request_id)

    def _lookup_pedido_mock(self, pedido_id: int) -> PedidoLookupResult:
        if pedido_id <= 0:
            return PedidoLookupResult(
                exists=False,
                is_eligible=False,
                status_code=404,
                message="Pedido no encontrado en ms-pedidos (stub)",
            )

        return PedidoLookupResult(
            exists=True,
            is_eligible=True,
            status_code=200,
            payload={"id": pedido_id, "estado": "aprobado"},
        )

    async def _lookup_pedido_http(self, pedido_id: int, request_id: str | None) -> PedidoLookupResult:
        base_url = self._settings.ped_base_url.rstrip("/")
        url = f"{base_url}/api/v1/pedidos/{pedido_id}"

        headers = {
            "X-App-Token": self._settings.ped_app_token,
        }
        if request_id:
            headers["X-Request-ID"] = request_id

        try:
            async with httpx.AsyncClient(timeout=self._settings.ped_timeout_seconds) as client:
                response = await client.get(url, headers=headers)
        except httpx.TimeoutException:
            return PedidoLookupResult(
                exists=False,
                is_eligible=False,
                status_code=503,
                message="Timeout consultando ms-pedidos",
            )
        except httpx.RequestError:
            return PedidoLookupResult(
                exists=False,
                is_eligible=False,
                status_code=503,
                message="ms-pedidos no disponible",
            )

        if response.status_code == 404:
            return PedidoLookupResult(
                exists=False,
                is_eligible=False,
                status_code=404,
                message="Pedido no encontrado en ms-pedidos",
            )

        if response.status_code >= 500:
            return PedidoLookupResult(
                exists=False,
                is_eligible=False,
                status_code=503,
                message="ms-pedidos no disponible",
            )

        if response.status_code != 200:
            return PedidoLookupResult(
                exists=False,
                is_eligible=False,
                status_code=response.status_code,
                message="Error consultando ms-pedidos",
            )

        raw_payload = response.json() if response.content else {}
        payload = raw_payload.get("data") if isinstance(raw_payload, dict) else None
        if not isinstance(payload, dict):
            payload = {}

        estado = payload.get("estado")
        if isinstance(estado, str) and estado.lower() in {"cancelado", "anulado"}:
            return PedidoLookupResult(
                exists=True,
                is_eligible=False,
                status_code=422,
                message=f"Pedido no elegible para entrega (estado={estado})",
                payload=payload,
            )

        return PedidoLookupResult(
            exists=True,
            is_eligible=True,
            status_code=200,
            payload=payload,
        )


pedidos_client = PedidosClient()
