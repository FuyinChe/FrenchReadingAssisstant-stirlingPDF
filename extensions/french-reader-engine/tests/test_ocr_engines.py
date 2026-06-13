def test_ocr_engines_endpoint():
    from fastapi.testclient import TestClient

    from french_reader.main import app

    client = TestClient(app)
    response = client.get("/french-reader/ocr/engines")
    assert response.status_code == 200
    body = response.json()
    assert "engines" in body
    assert isinstance(body["engines"], list)
