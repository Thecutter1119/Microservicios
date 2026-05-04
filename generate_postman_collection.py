import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "postman"
OUT_DIR.mkdir(exist_ok=True)


def ph(path: str) -> str:
    return re.sub(r"\{([^}]+)\}", r"{{\1}}", path)


SERVICES = [
    ("ms-autenticacion", "base_ms_autenticacion", "http://localhost:8101", "/api/v1", [
        ("POST", "/login", "Login"), ("POST", "/logout", "Logout"), ("POST", "/validar-sesion", "Validar Sesion"),
        ("GET", "/sesiones/activas", "Sesiones Activas"), ("POST", "/sesiones/{sesion_id}/forzar-cierre", "Forzar Cierre Sesion"),
        ("GET", "/historial-accesos", "Historial Accesos"), ("POST", "/tokens-aplicacion", "Crear Token Aplicacion"),
        ("GET", "/tokens-aplicacion", "Listar Tokens Aplicacion"), ("PUT", "/tokens-aplicacion/{token_id}", "Actualizar Token Aplicacion"),
        ("POST", "/tokens-aplicacion/{token_id}/desactivar", "Desactivar Token Aplicacion"),
    ]),
    ("ms-roles", "base_ms_roles", "http://localhost:8102", "/api/v1", [
        ("POST", "/roles", "Crear Rol"), ("GET", "/roles", "Listar Roles"), ("PUT", "/roles/{rol_id}", "Actualizar Rol"),
        ("POST", "/roles/{rol_id}/desactivar", "Desactivar Rol"), ("POST", "/permisos", "Crear Permiso"), ("GET", "/permisos", "Listar Permisos"),
        ("PUT", "/permisos/{permiso_id}", "Actualizar Permiso"), ("DELETE", "/permisos/{permiso_id}", "Eliminar Permiso"),
        ("POST", "/roles/{rol_id}/permisos", "Asignar Permisos a Rol"), ("DELETE", "/roles/{rol_id}/permisos/{permiso_id}", "Quitar Permiso de Rol"),
        ("POST", "/usuarios/{usuario_id}/roles", "Asignar Rol a Usuario"), ("GET", "/usuarios/{usuario_id}/roles", "Listar Roles de Usuario"),
        ("DELETE", "/usuarios/{usuario_id}/roles", "Quitar Rol a Usuario"), ("GET", "/validar-permiso", "Validar Permiso"),
        ("GET", "/permisos/por-modulo", "Permisos por Modulo"), ("GET", "/internal/usuarios/{usuario_id}/permisos", "Permisos Internos Usuario"),
    ]),
    ("ms-usuarios", "base_ms_usuarios", "http://localhost:8103", "/api/v1/usuarios", [
        ("POST", "", "Crear Usuario"), ("GET", "", "Listar Usuarios"), ("GET", "/{usuario_id}", "Obtener Usuario"),
        ("PUT", "/{usuario_id}", "Actualizar Usuario"), ("POST", "/{usuario_id}/desactivar", "Desactivar Usuario"),
        ("POST", "/{usuario_id}/estado", "Cambiar Estado Usuario"), ("GET", "/{usuario_id}/historial-estados", "Historial Estados Usuario"),
        ("POST", "/perfiles", "Crear Perfil"), ("GET", "/{usuario_id}/perfil", "Obtener Perfil"), ("PUT", "/{usuario_id}/perfil", "Actualizar Perfil"),
        ("GET", "/busqueda/avanzada", "Busqueda Avanzada"), ("GET", "/buscar/email/{email}", "Buscar por Email"),
        ("GET", "/buscar/documento/{numero_documento}", "Buscar por Documento"), ("GET", "/internal/username/{username}", "Consulta Interna por Username"),
        ("GET", "/internal/email/{email}", "Consulta Interna por Email"),
    ]),
    ("ms-inventario", "base_ms_inventario", "http://localhost:8104", "/api/v1", [
        ("POST", "/categorias", "Crear Categoria"), ("GET", "/categorias", "Listar Categorias"), ("PUT", "/categorias/{categoria_id}", "Actualizar Categoria"),
        ("POST", "/activos", "Crear Activo"), ("GET", "/activos", "Listar Activos"), ("GET", "/activos/{activo_id}", "Obtener Activo"),
        ("PUT", "/activos/{activo_id}", "Actualizar Activo"), ("POST", "/activos/{activo_id}/baja", "Dar de Baja Activo"),
        ("POST", "/movimientos", "Registrar Movimiento"), ("GET", "/activos/{activo_id}/movimientos", "Movimientos de Activo"),
        ("GET", "/activos/stock/bajo", "Activos Stock Bajo"), ("GET", "/depreciacion/{activo_id}", "Depreciacion Activo"),
    ]),
    ("ms-espacios", "base_ms_espacios", "http://localhost:8105", "/api/v1", [
        ("POST", "/tipos-espacio", "Crear Tipo Espacio"), ("GET", "/tipos-espacio", "Listar Tipos Espacio"), ("POST", "/espacios", "Crear Espacio"),
        ("GET", "/espacios", "Listar Espacios"), ("GET", "/espacios/{espacio_id}", "Obtener Espacio"), ("PUT", "/espacios/{espacio_id}", "Actualizar Espacio"),
        ("POST", "/espacios/{espacio_id}/estado", "Cambiar Estado Espacio"), ("GET", "/espacios/disponibles", "Espacios Disponibles"),
        ("POST", "/equipamiento/asignar", "Asignar Equipamiento"), ("DELETE", "/equipamiento/remover", "Remover Equipamiento"),
        ("GET", "/espacios/{espacio_id}/equipamiento", "Equipamiento de Espacio"), ("POST", "/mantenimientos", "Crear Mantenimiento"),
        ("GET", "/mantenimientos", "Listar Mantenimientos"), ("PUT", "/mantenimientos/{mantenimiento_id}", "Actualizar Mantenimiento"),
        ("POST", "/ocupacion", "Registrar Ocupacion"), ("GET", "/espacios/{espacio_id}/ocupacion", "Ocupacion de Espacio"),
    ]),
    ("ms-reservas", "base_ms_reservas", "http://localhost:8106", "/api/v1", [
        ("POST", "/reservas", "Crear Reserva"), ("GET", "/reservas", "Listar Reservas"), ("GET", "/reservas/{reserva_id}", "Obtener Reserva"),
        ("PUT", "/reservas/{reserva_id}", "Actualizar Reserva"), ("POST", "/reservas/{reserva_id}/confirmar", "Confirmar Reserva"),
        ("POST", "/reservas/{reserva_id}/cancelar", "Cancelar Reserva"), ("GET", "/disponibilidad", "Consultar Disponibilidad"),
        ("POST", "/politicas", "Crear Politica"), ("GET", "/politicas", "Listar Politicas"), ("PUT", "/politicas/{politica_id}", "Actualizar Politica"),
        ("POST", "/bloqueos", "Crear Bloqueo"), ("GET", "/bloqueos", "Listar Bloqueos"), ("DELETE", "/bloqueos/{bloqueo_id}", "Eliminar Bloqueo"),
    ]),
    ("ms-presupuesto", "base_ms_presupuesto", "http://localhost:8107", "/api/v1", [
        ("POST", "/presupuestos", "Crear Presupuesto"), ("GET", "/presupuestos", "Listar Presupuestos"), ("PUT", "/presupuestos/{presupuesto_id}", "Actualizar Presupuesto"),
        ("POST", "/presupuestos/{presupuesto_id}/aprobar", "Aprobar Presupuesto"), ("POST", "/partidas", "Crear Partida"), ("GET", "/partidas", "Listar Partidas"),
        ("PUT", "/partidas/{partida_id}", "Actualizar Partida"), ("GET", "/partidas/{partida_id}/saldo", "Saldo Partida"),
        ("POST", "/partidas/{partida_id}/consumir", "Consumir Partida"), ("POST", "/reasignaciones", "Crear Reasignacion"),
        ("POST", "/reasignaciones/{reasignacion_id}/aprobar", "Aprobar Reasignacion"), ("POST", "/reasignaciones/{reasignacion_id}/rechazar", "Rechazar Reasignacion"),
        ("GET", "/presupuestos/{presupuesto_id}/resumen", "Resumen Presupuesto"),
    ]),
    ("ms-gastos", "base_ms_gastos", "http://localhost:8108", "/api/v1", [
        ("POST", "/categorias", "Crear Categoria Gasto"), ("GET", "/categorias", "Listar Categorias Gasto"), ("POST", "/gastos", "Crear Gasto"),
        ("GET", "/gastos", "Listar Gastos"), ("PUT", "/gastos/{gasto_id}", "Actualizar Gasto"), ("POST", "/gastos/{gasto_id}/estado", "Cambiar Estado Gasto"),
        ("POST", "/novedades", "Crear Novedad"), ("GET", "/novedades", "Listar Novedades"), ("PUT", "/novedades/{novedad_id}", "Actualizar Novedad"),
        ("GET", "/aprobaciones", "Listar Aprobaciones"),
    ]),
    ("ms-facturacion", "base_ms_facturacion", "http://localhost:8109", "/api/v1", [
        ("POST", "/conceptos", "Crear Concepto"), ("GET", "/conceptos", "Listar Conceptos"), ("PUT", "/conceptos/{concepto_id}", "Actualizar Concepto"),
        ("POST", "/facturas", "Crear Factura"), ("GET", "/facturas", "Listar Facturas"), ("PUT", "/facturas/{factura_id}", "Actualizar Factura"),
        ("POST", "/facturas/{factura_id}/pagar", "Pagar Factura"), ("POST", "/facturas/{factura_id}/anular", "Anular Factura"),
        ("POST", "/facturas/actualizar-vencidas", "Actualizar Vencidas"), ("GET", "/estado-cuenta/{usuario_id}", "Estado de Cuenta"),
        ("POST", "/facturas/masivo/recurrente", "Facturacion Masiva Recurrente"),
    ]),
    ("ms-pedidos", "base_ms_pedidos", "http://localhost:8110", "/api/v1/pedidos", [
        ("POST", "", "Crear Pedido"), ("GET", "", "Listar Pedidos"), ("GET", "/{pedido_id}", "Obtener Pedido"), ("PUT", "/{pedido_id}", "Actualizar Pedido"),
        ("POST", "/{pedido_id}/avanzar-estado", "Avanzar Estado Pedido"), ("POST", "/{pedido_id}/cancelar", "Cancelar Pedido"),
        ("POST", "/{pedido_id}/items", "Agregar Item"), ("GET", "/{pedido_id}/items", "Listar Items"), ("PUT", "/{pedido_id}/items/{item_id}", "Actualizar Item"),
        ("DELETE", "/{pedido_id}/items/{item_id}", "Eliminar Item"), ("POST", "/{pedido_id}/recepciones", "Registrar Recepcion"),
        ("GET", "/{pedido_id}/historial", "Historial Pedido"),
    ]),
    ("ms-domicilios", "base_ms_domicilios", "http://localhost:8111", "", [
        ("GET", "/health", "Health"), ("POST", "/api/v1/repartidores", "Crear Repartidor"), ("GET", "/api/v1/repartidores", "Listar Repartidores por Zona"),
        ("GET", "/api/v1/repartidores/{repartidor_id}", "Obtener Repartidor"), ("PUT", "/api/v1/repartidores/{repartidor_id}", "Actualizar Repartidor"),
        ("POST", "/api/v1/entregas", "Crear Entrega"), ("GET", "/api/v1/entregas/{entrega_id}", "Obtener Entrega"), ("PUT", "/api/v1/entregas/{entrega_id}", "Actualizar Entrega"),
        ("POST", "/api/v1/entregas/{entrega_id}/asignar", "Asignar Repartidor"), ("PATCH", "/api/v1/entregas/{entrega_id}/estado", "Actualizar Estado Entrega"),
        ("POST", "/api/v1/entregas/{entrega_id}/seguimiento", "Registrar Seguimiento"), ("GET", "/api/v1/entregas/{entrega_id}/seguimiento", "Consultar Seguimiento"),
        ("POST", "/api/v1/entregas/{entrega_id}/calificaciones", "Calificar Entrega"),
    ]),
    ("ms-proveedores", "base_ms_proveedores", "http://localhost:8112", "", [
        ("GET", "/", "Root"), ("GET", "/health", "Health"), ("POST", "/proveedores", "Crear Proveedor"), ("GET", "/proveedores", "Listar Proveedores"),
        ("GET", "/proveedores/{proveedor_id}", "Obtener Proveedor"), ("PUT", "/proveedores/{proveedor_id}", "Actualizar Proveedor"),
        ("POST", "/proveedores/{proveedor_id}/desactivar", "Desactivar Proveedor"), ("POST", "/contratos", "Crear Contrato"), ("GET", "/contratos/{contrato_id}", "Obtener Contrato"),
        ("GET", "/proveedores/{proveedor_id}/contratos", "Contratos por Proveedor"), ("PUT", "/contratos/{contrato_id}", "Actualizar Contrato"),
        ("GET", "/contratos/proximos-vencer", "Contratos Proximos a Vencer"), ("GET", "/proveedores/{proveedor_id}/contrato/vigente", "Contrato Vigente"),
        ("POST", "/evaluaciones", "Crear Evaluacion"), ("GET", "/proveedores/{proveedor_id}/evaluaciones", "Evaluaciones por Proveedor"),
        ("POST", "/cotizaciones", "Crear Cotizacion"), ("PUT", "/cotizaciones/{cotizacion_id}", "Actualizar Cotizacion"), ("GET", "/cotizaciones/comparar", "Comparar Cotizaciones"),
        ("POST", "/documentos", "Crear Documento"), ("GET", "/proveedores/{proveedor_id}/documentos", "Documentos por Proveedor"), ("GET", "/documentos/proximos-vencer", "Documentos Proximos a Vencer"),
    ]),
    ("ms-programas", "base_ms_programas", "http://localhost:8113", "/api/v1", [
        ("POST", "/programas", "Crear Programa"), ("GET", "/programas", "Listar Programas"), ("PUT", "/programas/{programa_id}", "Actualizar Programa"),
        ("POST", "/programas/{programa_id}/desactivar", "Desactivar Programa"), ("POST", "/asignaturas", "Crear Asignatura"), ("GET", "/asignaturas", "Listar Asignaturas"),
        ("PUT", "/asignaturas/{asignatura_id}", "Actualizar Asignatura"), ("POST", "/prerrequisitos", "Crear Prerrequisito"), ("DELETE", "/prerrequisitos", "Eliminar Prerrequisito"),
        ("GET", "/malla/{programa_id}", "Malla por Programa"), ("POST", "/mallas-version", "Crear Version Malla"), ("GET", "/mallas-version/{programa_id}", "Versiones Malla"),
        ("GET", "/internal/asignaturas/{asignatura_id}", "Consulta Interna Asignatura"), ("GET", "/internal/asignaturas/{asignatura_id}/prerrequisitos", "Consulta Interna Prerrequisitos"),
    ]),
    ("ms-matriculas", "base_ms_matriculas", "http://localhost:8114", "/api/v1", [
        ("POST", "/periodos", "Crear Periodo"), ("GET", "/periodos", "Listar Periodos"), ("PUT", "/periodos/{periodo_id}", "Actualizar Periodo"),
        ("POST", "/periodos/{periodo_id}/estado", "Cambiar Estado Periodo"), ("POST", "/matriculas", "Crear Matricula"), ("GET", "/matriculas", "Listar Matriculas"),
        ("PUT", "/matriculas/{matricula_id}", "Actualizar Matricula"), ("POST", "/inscripciones/validar-previo", "Validar Inscripcion"),
        ("POST", "/inscripciones", "Crear Inscripcion"), ("POST", "/inscripciones/{inscripcion_id}/cancelar", "Cancelar Inscripcion"),
        ("GET", "/asignaturas/{asignatura_id}/inscritos", "Inscritos por Asignatura"), ("GET", "/internal/matriculas/{estudiante_id}/inscripciones", "Consulta Interna Inscripciones"),
    ]),
    ("ms-calificaciones", "base_ms_calificaciones", "http://localhost:8115", "/api/v1", [
        ("POST", "/cortes", "Crear Corte"), ("GET", "/cortes", "Listar Cortes"), ("POST", "/notas", "Crear Nota"), ("PUT", "/notas/{nota_id}", "Actualizar Nota"),
        ("GET", "/inscripciones/{inscripcion_id}/notas", "Notas por Inscripcion"), ("GET", "/cortes/{corte_id}/notas", "Notas por Corte"),
        ("GET", "/inscripciones/{inscripcion_id}/definitiva", "Definitiva Inscripcion"), ("POST", "/promedios/recalcular", "Recalcular Promedios"),
        ("GET", "/promedios/estudiante/{estudiante_id}", "Promedio Estudiante"), ("GET", "/promedios/bajo-rendimiento", "Bajo Rendimiento"),
    ]),
    ("ms-horarios", "base_ms_horarios", "http://localhost:8116", "/api/v1", [
        ("POST", "/franjas", "Crear Franja"), ("GET", "/franjas", "Listar Franjas"), ("PUT", "/franjas/{franja_id}", "Actualizar Franja"),
        ("POST", "/franjas/{franja_id}/cancelar", "Cancelar Franja"), ("POST", "/asignaciones-docente", "Asignar Docente"), ("GET", "/asignaciones-docente", "Listar Asignaciones Docente"),
        ("GET", "/docentes/{docente_id}/horario", "Horario Docente"), ("GET", "/espacios/{espacio_id}/ocupacion", "Ocupacion Espacio"), ("GET", "/franjas/conflicto-espacio", "Conflicto Espacio"),
    ]),
    ("ms-notificaciones", "base_ms_notificaciones", "http://localhost:8117", "/api/v1", [
        ("POST", "/plantillas", "Crear Plantilla"), ("GET", "/plantillas", "Listar Plantillas"), ("PUT", "/plantillas/{plantilla_id}", "Actualizar Plantilla"),
        ("POST", "/plantillas/{plantilla_id}/desactivar", "Desactivar Plantilla"), ("POST", "/preferencias", "Crear Preferencia"), ("GET", "/preferencias/{usuario_id}", "Consultar Preferencia"),
        ("POST", "/enviar", "Enviar Notificacion"), ("POST", "/enviar-con-plantilla", "Enviar con Plantilla"), ("POST", "/enviar-masivo", "Enviar Masivo"),
        ("GET", "/pendientes", "Notificaciones Pendientes"), ("POST", "/notificaciones/{notificacion_id}/leida", "Marcar Leida"), ("GET", "/usuarios/{usuario_id}/no-leidas", "No Leidas por Usuario"),
    ]),
    ("ms-auditoria", "base_ms_auditoria", "http://localhost:8118", "/api/v1", [
        ("POST", "/logs", "Crear Log"), ("POST", "/log", "Crear Log Alias"), ("GET", "/traza/{request_id}", "Trazabilidad por Request ID"),
        ("GET", "/logs", "Listar Logs"), ("GET", "/retencion", "Consultar Retencion"), ("PUT", "/retencion", "Actualizar Retencion"),
        ("POST", "/rotacion/ejecutar", "Ejecutar Rotacion"), ("POST", "/estadisticas/recalcular", "Recalcular Estadisticas"), ("GET", "/estadisticas", "Consultar Estadisticas"),
    ]),
    ("ms-reportes", "base_ms_reportes", "http://localhost:8119", "", [
        ("GET", "/health", "Health"), ("GET", "/info", "Info"), ("POST", "/api/v1/plantillas", "Crear Plantilla Reporte"), ("GET", "/api/v1/plantillas", "Listar Plantillas Reporte"),
        ("GET", "/api/v1/plantillas/{plantilla_id}", "Obtener Plantilla Reporte"), ("PUT", "/api/v1/plantillas/{plantilla_id}", "Actualizar Plantilla Reporte"),
        ("DELETE", "/api/v1/plantillas/{plantilla_id}", "Eliminar Plantilla Reporte"), ("POST", "/api/v1/reportes", "Solicitar Reporte"),
        ("GET", "/api/v1/reportes", "Listar Reportes"), ("GET", "/api/v1/reportes/{reporte_id}", "Estado Reporte"), ("GET", "/api/v1/reportes/{reporte_id}/descargar", "Descargar Reporte"),
        ("POST", "/api/v1/reportes/{reporte_id}/invalidar-cache", "Invalidar Cache Reporte"), ("POST", "/api/v1/programaciones", "Crear Programacion"),
        ("GET", "/api/v1/programaciones", "Listar Programaciones"), ("GET", "/api/v1/programaciones/{prog_id}", "Obtener Programacion"),
        ("PUT", "/api/v1/programaciones/{prog_id}", "Actualizar Programacion"), ("POST", "/api/v1/programaciones/{prog_id}/desactivar", "Desactivar Programacion"),
        ("POST", "/api/v1/programaciones/{prog_id}/reactivar", "Reactivar Programacion"), ("POST", "/api/v1/programaciones/{prog_id}/ejecutar", "Ejecutar Programacion"),
    ]),
]

EXAMPLES = {
    ("ms-roles", "POST", "/roles"): {"nombre": "Administrador", "descripcion": "Rol administrador"},
    ("ms-usuarios", "POST", ""): {"username": "admin.erp", "email": "admin@erp.local", "password_encrypted": "TU_PASSWORD_ENCRIPTADO", "rol_principal_id": 1},
    ("ms-autenticacion", "POST", "/login"): {"login": "admin.erp", "password_encrypted": "TU_PASSWORD_ENCRIPTADO"},
    ("ms-inventario", "POST", "/categorias"): {"nombre": "Equipos", "descripcion": "Categoria equipos"},
    ("ms-inventario", "POST", "/activos"): {"codigo_interno": "INV-001", "nombre": "Portatil", "categoria_id": 1, "precio_adquisicion": 2500000, "fecha_adquisicion": "2026-01-10", "vida_util_meses": 36, "stock_actual": 10, "stock_minimo": 2},
    ("ms-pedidos", "POST", ""): {"proveedor_id": 1, "observaciones": "Pedido de prueba"},
    ("ms-pedidos", "POST", "/{pedido_id}/items"): {"activo_id": 1, "descripcion": "Portatil", "cantidad_solicitada": 2, "valor_unitario": 2500000},
    ("ms-domicilios", "POST", "/api/v1/repartidores"): {"usuario_id": 1, "nombre": "Juan Repartidor", "telefono": "3001112233", "tipo_vehiculo": "moto", "placa_vehiculo": "ABC123", "zona_cobertura": "Centro"},
    ("ms-domicilios", "POST", "/api/v1/entregas"): {"pedido_id": 1, "origen": "Campus Norte", "destino": "Centro", "observaciones": "Entrega urgente"},
}

SAVE_VARS = {
    "Crear Rol": "rol_id",
    "Crear Usuario": "usuario_id",
    "Crear Categoria": "categoria_id",
    "Crear Activo": "activo_id",
    "Crear Pedido": "pedido_id",
    "Agregar Item": "item_id",
    "Crear Repartidor": "repartidor_id",
    "Crear Entrega": "entrega_id",
    "Crear Presupuesto": "presupuesto_id",
    "Crear Partida": "partida_id",
    "Crear Gasto": "gasto_id",
    "Crear Concepto": "concepto_id",
    "Crear Factura": "factura_id",
    "Crear Programa": "programa_id",
    "Crear Asignatura": "asignatura_id",
    "Crear Periodo": "periodo_id",
    "Crear Matricula": "matricula_id",
    "Crear Corte": "corte_id",
    "Crear Plantilla": "plantilla_id",
    "Solicitar Reporte": "reporte_id",
    "Crear Programacion": "prog_id",
}


def mk_tests(save_var: str | None = None):
    lines = [
        "pm.test('status < 500', function () { pm.expect(pm.response.code).to.be.below(500); });",
        "let data = null;",
        "try { data = pm.response.json(); } catch (e) {}",
        "if (data && data.request_id) { pm.collectionVariables.set('last_request_id', data.request_id); }",
    ]
    if save_var:
        lines.append(f"if (data && data.data && data.data.id !== undefined) {{ pm.collectionVariables.set('{save_var}', data.data.id); }}")
    return {"listen": "test", "script": {"type": "text/javascript", "exec": lines}}


def mk_req(svar: str, prefix: str, method: str, ep: str, name: str, body: dict | None, save_var: str | None):
    path = (prefix + ep) if prefix else ep
    path = path if path else "/"
    raw = f"{{{{{svar}}}}}{ph(path)}"
    req = {
        "name": name,
        "event": [mk_tests(save_var)],
        "request": {
            "method": method,
            "header": [
                {"key": "Content-Type", "value": "application/json", "type": "text"},
                {"key": "Authorization", "value": "Bearer {{auth_token}}", "type": "text"},
                {"key": "X-Request-ID", "value": "{{request_id}}", "type": "text"},
            ],
            "url": {"raw": raw, "host": [f"{{{{{svar}}}}}"]},
        },
        "response": [],
    }
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        payload = body if body is not None else {"TODO": "Completar body segun contrato"}
        req["request"]["body"] = {"mode": "raw", "raw": json.dumps(payload, ensure_ascii=False, indent=2), "options": {"raw": {"language": "json"}}}
    return req


items = []
for sname, svar, surl, prefix, endpoints in SERVICES:
    folder_items = []
    if not any(ep == "/health" for _, ep, _ in endpoints):
        folder_items.append(mk_req(svar, "", "GET", "/health", "Health", None, None))
    for method, ep, label in endpoints:
        body = EXAMPLES.get((sname, method, ep))
        save_var = SAVE_VARS.get(label)
        folder_items.append(mk_req(svar, prefix, method, ep, label, body, save_var))
    items.append({"name": f"Individual - {sname}", "item": folder_items})

colectivo = [
    mk_req("base_ms_roles", "", "GET", "/health", "[Flujo Seguridad] Health Roles", None, None),
    mk_req("base_ms_usuarios", "", "GET", "/health", "[Flujo Seguridad] Health Usuarios", None, None),
    mk_req("base_ms_autenticacion", "", "GET", "/health", "[Flujo Seguridad] Health Auth", None, None),
    mk_req("base_ms_roles", "/api/v1", "POST", "/roles", "[Flujo Seguridad] Crear Rol", {"nombre": "Administrador", "descripcion": "Rol de pruebas"}, "rol_id"),
    mk_req("base_ms_usuarios", "/api/v1/usuarios", "POST", "", "[Flujo Seguridad] Crear Usuario", {"username": "admin.erp", "email": "admin@erp.local", "password_encrypted": "TU_PASSWORD_ENCRIPTADO", "rol_principal_id": "{{rol_id}}"}, "usuario_id"),
    mk_req("base_ms_roles", "/api/v1", "POST", "/usuarios/{usuario_id}/roles", "[Flujo Seguridad] Asignar Rol Usuario", {"rol_id": "{{rol_id}}", "assigned_by": 1}, None),
    mk_req("base_ms_autenticacion", "/api/v1", "POST", "/login", "[Flujo Seguridad] Login", {"login": "admin.erp", "password_encrypted": "TU_PASSWORD_ENCRIPTADO"}, None),
    mk_req("base_ms_autenticacion", "/api/v1", "POST", "/validar-sesion", "[Flujo Seguridad] Validar Sesion", {"token": "{{auth_token}}"}, None),
    mk_req("base_ms_inventario", "/api/v1", "POST", "/categorias", "[Flujo Recursos] Crear Categoria", {"nombre": "Laboratorio", "descripcion": "Categoria QA"}, "categoria_id"),
    mk_req("base_ms_inventario", "/api/v1", "POST", "/activos", "[Flujo Recursos] Crear Activo", {"codigo_interno": "INV-QA-001", "nombre": "VideoBeam", "categoria_id": "{{categoria_id}}", "precio_adquisicion": 1200000, "fecha_adquisicion": "2026-01-10", "vida_util_meses": 36, "stock_actual": 3, "stock_minimo": 1}, "activo_id"),
    mk_req("base_ms_presupuesto", "/api/v1", "POST", "/presupuestos", "[Flujo Financiero] Crear Presupuesto", {"nombre": "Presupuesto QA 2026", "periodo": "2026-1", "monto_total": 50000000}, "presupuesto_id"),
    mk_req("base_ms_auditoria", "/api/v1", "GET", "/traza/{request_id}", "[Flujo Transversal] Consultar Trazabilidad", None, None),
]
items.append({"name": "Colectivo - Flujos Integrados", "item": colectivo})

collection_vars = [
    {"key": "request_id", "value": "ERP-QA-001"},
    {"key": "auth_token", "value": ""},
    {"key": "last_request_id", "value": ""},
    {"key": "rol_id", "value": "1"},
    {"key": "usuario_id", "value": "1"},
    {"key": "categoria_id", "value": "1"},
    {"key": "activo_id", "value": "1"},
    {"key": "pedido_id", "value": "1"},
    {"key": "item_id", "value": "1"},
    {"key": "repartidor_id", "value": "1"},
    {"key": "entrega_id", "value": "1"},
    {"key": "presupuesto_id", "value": "1"},
    {"key": "partida_id", "value": "1"},
    {"key": "gasto_id", "value": "1"},
    {"key": "concepto_id", "value": "1"},
    {"key": "factura_id", "value": "1"},
    {"key": "programa_id", "value": "1"},
    {"key": "asignatura_id", "value": "1"},
    {"key": "periodo_id", "value": "1"},
    {"key": "matricula_id", "value": "1"},
    {"key": "inscripcion_id", "value": "1"},
    {"key": "corte_id", "value": "1"},
    {"key": "nota_id", "value": "1"},
    {"key": "plantilla_id", "value": "1"},
    {"key": "reporte_id", "value": "1"},
    {"key": "prog_id", "value": "1"},
]
for _, svar, surl, _, _ in SERVICES:
    collection_vars.append({"key": svar, "value": surl})

collection = {
    "info": {
        "name": "ERP Universitario - Microservicios (Individual + Colectivo)",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        "description": "Coleccion basada en endpoints reales del codigo. Incluye pruebas individuales por microservicio y flujos colectivos base.",
    },
    "item": items,
    "variable": collection_vars,
}

environment = {
    "id": "erp-universitario-local",
    "name": "ERP Universitario Local Docker",
    "values": [{"key": svar, "value": surl, "enabled": True} for _, svar, surl, _, _ in SERVICES] + [
        {"key": "request_id", "value": "ERP-QA-001", "enabled": True},
        {"key": "auth_token", "value": "", "enabled": True},
    ],
    "_postman_variable_scope": "environment",
    "_postman_exported_at": "2026-05-04T00:00:00.000Z",
    "_postman_exported_using": "GPT-5.3-Codex",
}

collection_path = OUT_DIR / "ERP_Microservicios_Universitario.postman_collection.json"
environment_path = OUT_DIR / "ERP_Microservicios_Universitario.local.postman_environment.json"
collection_path.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
environment_path.write_text(json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8")

print(collection_path)
print(environment_path)
