from dataclasses import dataclass

from french_reader.config import settings


@dataclass(frozen=True)
class LlmConfig:
    api_key: str
    base_url: str
    model: str
    key_source: str


def resolve_llm_api_key(api_key_override: str | None = None) -> str | None:
    override = (api_key_override or "").strip()
    if override:
        return override
    return settings.resolve_llm_api_key()


def is_llm_configured(api_key_override: str | None = None) -> bool:
    return bool(resolve_llm_api_key(api_key_override))


def resolve_llm_config(api_key_override: str | None = None) -> LlmConfig:
    override = (api_key_override or "").strip()
    server_key = settings.resolve_llm_api_key()
    api_key = override or server_key
    if not api_key:
        raise ValueError("LLM API key is not configured")

    key_source = "client" if override else "server"
    return LlmConfig(
        api_key=api_key,
        base_url=settings.llm_base_url.rstrip("/"),
        model=settings.llm_model,
        key_source=key_source,
    )


def get_ai_status(api_key_override: str | None = None) -> dict[str, str | bool]:
    server_configured = is_llm_configured()
    client_configured = bool((api_key_override or "").strip())
    configured = is_llm_configured(api_key_override)

    if configured:
        config = resolve_llm_config(api_key_override)
        detail = (
            "LLM ready (your API key)"
            if config.key_source == "client"
            else "LLM ready (server configuration)"
        )
        return {
            "ready": True,
            "server_configured": server_configured,
            "client_configured": client_configured,
            "provider": "openai-compatible",
            "model": config.model,
            "detail": detail,
        }

    return {
        "ready": False,
        "server_configured": server_configured,
        "client_configured": client_configured,
        "provider": "openai-compatible",
        "model": "",
        "detail": "Set FRENCH_READER_LLM_API_KEY in .env or paste your Kimi API key in Settings",
    }
