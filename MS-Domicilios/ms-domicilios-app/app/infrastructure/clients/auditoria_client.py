import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger("ms_domicilios.audit")


class AuditoriaClient:
    async def send_log(self, payload: dict) -> None:
        # Stub inicial fire-and-forget.
        await asyncio.sleep(0)
        logger.info("AUD_STUB payload=%s", payload)


auditoria_client = AuditoriaClient()


def fire_and_forget_audit(payload: dict) -> None:
    async def _send() -> None:
        try:
            await auditoria_client.send_log(payload)
        except Exception as exc:  # pragma: no cover - fallback defensivo
            logger.warning("AUD_FALLBACK_LOCAL error=%s payload=%s", exc, payload)

    try:
        asyncio.create_task(_send())
    except RuntimeError:
        logger.warning(
            "AUD_FALLBACK_NO_LOOP payload=%s ts=%s",
            payload,
            datetime.now(timezone.utc).isoformat(),
        )
