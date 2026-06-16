from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from french_reader.config import settings
from french_reader.plugin_version import get_plugin_version_info, get_plugin_version_string
from french_reader.router import router

_plugin = get_plugin_version_info()
app = FastAPI(title="French Reader Engine", version=get_plugin_version_string())

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        # Tauri / WebView2 desktop origins vary by OS (tauri.localhost, ipc.localhost, ports).
        allow_origin_regex=(
            r"^https?://([\w-]+\.)?localhost(:\d+)?$"
            r"|^https?://127\.0\.0\.1(:\d+)?$"
            r"|^tauri://"
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str | bool | dict]:
    return {
        "status": "ok",
        "enabled": settings.enabled,
        "service": "french-reader-engine",
        "plugin": _plugin,
    }
