from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from french_reader.config import settings
from french_reader.router import router

app = FastAPI(title="French Reader Engine", version="0.1.0")

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {"status": "ok", "enabled": settings.enabled, "service": "french-reader-engine"}
