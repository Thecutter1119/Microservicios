from app.db.session import Base, SessionLocal, engine
from app.models.entities import Permiso, Rol, RolPermiso, UsuarioRol  # noqa: F401


BASIC_ROLES = ["Administrador", "Docente", "Estudiante", "Operador"]
BASIC_PERMISSIONS = [
    {
        "codigo": "AUTH_VALIDATE_SESSION",
        "nombre": "Validar sesion",
        "descripcion": "Permite validar sesiones de usuario",
        "modulo": "Seguridad",
        "microservicio_origen": "ms-autenticacion",
        "funcionalidad": "Validacion de sesion",
        "metodo_operacion": "consulta",
    },
    {
        "codigo": "ROL_VALIDATE_PERMISSION",
        "nombre": "Validar permiso",
        "descripcion": "Permite validar permisos por rol",
        "modulo": "Seguridad",
        "microservicio_origen": "ms-roles",
        "funcionalidad": "Validacion de permiso",
        "metodo_operacion": "consulta",
    },
    {
        "codigo": "USR_CREATE",
        "nombre": "Crear usuario",
        "descripcion": "Permite crear usuarios",
        "modulo": "Seguridad",
        "microservicio_origen": "ms-usuarios",
        "funcionalidad": "Creacion de usuario",
        "metodo_operacion": "creacion",
    },
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for role_name in BASIC_ROLES:
            if not db.query(Rol).filter(Rol.nombre == role_name).first():
                db.add(Rol(nombre=role_name, descripcion=f"Rol base: {role_name}"))
        db.commit()
        for perm in BASIC_PERMISSIONS:
            if not db.query(Permiso).filter(Permiso.codigo == perm["codigo"]).first():
                db.add(Permiso(**perm))
        db.commit()
    finally:
        db.close()
