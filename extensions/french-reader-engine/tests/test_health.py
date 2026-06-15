from fastapi.testclient import TestClient

from french_reader.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "french-reader-engine"


def test_french_reader_status():
    response = client.get("/french-reader/status")
    assert response.status_code == 200
    assert response.json()["module"] == "french-reader"
