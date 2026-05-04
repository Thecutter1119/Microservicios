from dataclasses import dataclass


@dataclass(slots=True)
class PermissionResult:
    authorized: bool
    permission_code: str
    message: str | None = None


class RolClient:
    def check_permission(self, role: str, permission_code: str) -> PermissionResult:
        raise NotImplementedError("ROL client stub: pending integration with ms-roles")
