from dataclasses import dataclass


@dataclass(slots=True)
class AuthSessionResult:
    valid: bool
    user_id: int | None = None
    role: str | None = None
    message: str | None = None


class AuthClient:
    def validate_session(self, token: str) -> AuthSessionResult:
        raise NotImplementedError("AUTH client stub: pending integration with ms-autenticacion")
