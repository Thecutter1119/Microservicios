from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database import Base, get_db
from app.main import app


@pytest.fixture
def client(tmp_path: Path):
    db_file = tmp_path / "fase2.sqlite"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _auth(role_token: str = "admin") -> dict[str, str]:
    return {"Authorization": f"Bearer {role_token}"}


def test_repartidor_crud_base(client: TestClient):
    create_payload = {
        "usuario_id": 109,
        "nombre": "Pedro Salazar Torres",
        "telefono": "3178885566",
        "tipo_vehiculo": "moto",
        "placa_vehiculo": "MOT-555",
        "zona_cobertura": "Norte",
    }

    create_res = client.post("/api/v1/repartidores", json=create_payload, headers=_auth("admin"))
    assert create_res.status_code == 201
    assert create_res.json()["success"] is True

    duplicate_res = client.post("/api/v1/repartidores", json=create_payload, headers=_auth("admin"))
    assert duplicate_res.status_code == 409

    repartidor_id = create_res.json()["data"]["id"]
    get_res = client.get(f"/api/v1/repartidores/{repartidor_id}", headers=_auth("operador"))
    assert get_res.status_code == 200
    assert get_res.json()["data"]["placa_vehiculo"] == "MOT-555"


def test_flujo_entrega_seguimiento_calificacion(client: TestClient):
    repartidor = client.post(
        "/api/v1/repartidores",
        json={
            "usuario_id": 221,
            "nombre": "Sara Jimenez",
            "telefono": "3001234567",
            "tipo_vehiculo": "moto",
            "placa_vehiculo": "ABC-123",
            "zona_cobertura": "Norte",
        },
        headers=_auth("admin"),
    )
    repartidor_id = repartidor.json()["data"]["id"]

    entrega = client.post(
        "/api/v1/entregas",
        json={"pedido_id": 9001, "origen": "Bodega Norte", "destino": "Norte - Calle 100"},
        headers=_auth("operador"),
    )
    assert entrega.status_code == 201
    entrega_id = entrega.json()["data"]["id"]

    asignacion = client.post(
        f"/api/v1/entregas/{entrega_id}/asignar",
        json={"repartidor_id": repartidor_id},
        headers=_auth("operador"),
    )
    assert asignacion.status_code == 200

    estado_camino = client.patch(
        f"/api/v1/entregas/{entrega_id}/estado",
        json={"estado": "en_camino", "latitud": 4.65, "longitud": -74.05},
        headers=_auth("operador"),
    )
    assert estado_camino.status_code == 200

    seguimiento = client.post(
        f"/api/v1/entregas/{entrega_id}/seguimiento",
        json={"latitud": 4.651, "longitud": -74.051, "descripcion": "Punto manual"},
        headers=_auth("operador"),
    )
    assert seguimiento.status_code == 201

    estado_final = client.patch(
        f"/api/v1/entregas/{entrega_id}/estado",
        json={"estado": "entregada", "latitud": 4.652, "longitud": -74.052},
        headers=_auth("operador"),
    )
    assert estado_final.status_code == 200

    calificacion = client.post(
        f"/api/v1/entregas/{entrega_id}/calificaciones",
        json={"puntaje": 5, "comentario": "Excelente servicio"},
        headers=_auth("solicitante-01"),
    )
    assert calificacion.status_code == 201
    assert calificacion.json()["data"]["puntaje"] == 5


def test_security_requires_authorization_header(client: TestClient):
    response = client.get("/api/v1/repartidores/1")
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_crear_entrega_rechaza_pedido_no_existente_stub(client: TestClient):
    response = client.post(
        "/api/v1/entregas",
        json={"pedido_id": 0, "origen": "Bodega", "destino": "Norte - Calle 10"},
        headers=_auth("operador"),
    )

    assert response.status_code == 404
    assert response.json()["success"] is False


def test_no_permite_cambiar_estado_sin_repartidor_asignado(client: TestClient):
    entrega = client.post(
        "/api/v1/entregas",
        json={"pedido_id": 9100, "origen": "Bodega", "destino": "Norte - Calle 90"},
        headers=_auth("operador"),
    )
    assert entrega.status_code == 201

    entrega_id = entrega.json()["data"]["id"]
    cambio_estado = client.patch(
        f"/api/v1/entregas/{entrega_id}/estado",
        json={"estado": "en_camino", "latitud": 4.6, "longitud": -74.0},
        headers=_auth("operador"),
    )

    assert cambio_estado.status_code == 422
    assert "sin repartidor asignado" in cambio_estado.json()["message"]
