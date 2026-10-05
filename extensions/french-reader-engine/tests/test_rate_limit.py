from fastapi import FastAPI
from fastapi.testclient import TestClient

from french_reader.rate_limit import RateLimitMiddleware


def _limited_client(max_per_minute: int) -> TestClient:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, max_per_minute=max_per_minute)

    @app.post("/french-reader/ocr/region")
    def ocr_region() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


def test_rate_limit_blocks_repeated_posts():
    client = _limited_client(2)
    first = client.post("/french-reader/ocr/region")
    second = client.post("/french-reader/ocr/region")
    third = client.post("/french-reader/ocr/region")
    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "Rate limit" in third.json()["detail"]


def test_rate_limit_skips_health_gets():
    client = _limited_client(1)
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200
