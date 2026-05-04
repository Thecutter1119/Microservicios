class RolClient:
    async def has_permission(self, role: str | None, permission_code: str) -> bool:
        # Stub fase 2: matriz de permisos minima para flujos funcionales.
        if not role:
            return False

        matrix = {
            "admin_logistico": "*",
            "operador_logistico": {
                "dom.repartidores.consultar",
                "dom.entregas.crear",
                "dom.entregas.consultar",
                "dom.entregas.actualizar",
                "dom.entregas.asignar",
                "dom.entregas.estado",
                "dom.seguimiento.consultar",
                "dom.seguimiento.registrar",
            },
            "solicitante": {
                "dom.entregas.consultar",
                "dom.seguimiento.consultar",
                "dom.calificaciones.registrar",
            },
        }

        allowed = matrix.get(role)
        if allowed == "*":
            return True
        if isinstance(allowed, set):
            return permission_code in allowed
        return False
