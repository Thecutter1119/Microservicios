from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.infrastructure.clients.aud import AudClient


@dataclass(slots=True)
class AuditDispatchResult:
    queued: bool
    fallback_used: bool
    message: str


class AuditService:
    def __init__(self, client: AudClient | None = None) -> None:
        self.client = client or AudClient()

    async def _send(self, payload: dict[str, Any]) -> AuditDispatchResult:
        try:
            self.client.send_log(payload)
            return AuditDispatchResult(queued=True, fallback_used=False, message="Audit queued")
        except NotImplementedError:
            self._write_local_fallback(payload)
            return AuditDispatchResult(
                queued=False,
                fallback_used=True,
                message="Audit fallback written locally",
            )

    def dispatch(self, payload: dict[str, Any]) -> AuditDispatchResult:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            self._write_local_fallback(payload)
            return AuditDispatchResult(queued=False, fallback_used=True, message="Audit fallback written locally")

        loop.create_task(self._send(payload))
        return AuditDispatchResult(queued=True, fallback_used=False, message="Audit scheduled")

    @staticmethod
    def _write_local_fallback(payload: dict[str, Any]) -> None:
        fallback_dir = Path("logs")
        fallback_dir.mkdir(exist_ok=True)
        fallback_file = fallback_dir / "audit-fallback.log"
        with fallback_file.open("a", encoding="utf-8") as file_handle:
            file_handle.write(f"{payload!r}\n")
