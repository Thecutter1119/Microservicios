from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_standard_response() -> None:
    response = client.get("/health")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert "request_id" in body
    assert "timestamp" in body
    assert body["data"]["status"] == "ok"


def test_health_reuses_request_id_header() -> None:
    response = client.get("/health", headers={"X-Request-ID": "DOM-test-123"})
    body = response.json()

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "DOM-test-123"
    assert body["request_id"] == "DOM-test-123"
