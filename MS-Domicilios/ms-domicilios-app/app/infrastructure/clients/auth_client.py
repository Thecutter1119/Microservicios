from dataclasses import dataclass


@dataclass
class SessionValidationResult:
    is_valid: bool
    user_id: int | None
    role: str | None


class AuthClient:
    async def validate_session(self, token: str | None) -> SessionValidationResult:
        # Stub fase 2: token "invalid" simula sesion expirada.
        if not token or token.lower() == "invalid":
            return SessionValidationResult(is_valid=False, user_id=None, role=None)

        if token.lower().startswith("solicitante"):
            return SessionValidationResult(is_valid=True, user_id=3001, role="solicitante")
        if token.lower().startswith("operador"):
            return SessionValidationResult(is_valid=True, user_id=2001, role="operador_logistico")
        return SessionValidationResult(is_valid=True, user_id=1001, role="admin_logistico")
