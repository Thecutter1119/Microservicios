from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AuditResult:
    queued: bool
    message: str | None = None


class AudClient:
    def send_log(self, payload: dict[str, Any]) -> AuditResult:
        raise NotImplementedError("AUD client stub: pending integration with ms-auditoria")
