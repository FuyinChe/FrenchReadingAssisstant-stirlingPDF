from dataclasses import dataclass

from french_reader.config import settings
from french_reader.llm_providers import (
    DEFAULT_PROVIDER_ID,
    get_llm_provider,
    list_llm_providers,
    resolve_client_llm_endpoint,
)


@dataclass(frozen=True)
class LlmConfig:
    api_key: str
    base_url: str
    model: str
    provider_id: str
    key_source: str


def resolve_llm_api_key(api_key_override: str | None = None) -> str | None:
    override = (api_key_override or "").strip()
    if override:
        return override
    return settings.resolve_llm_api_key()


def is_llm_configured(api_key_override: str | None = None) -> bool:
    return bool(resolve_llm_api_key(api_key_override))


def resolve_llm_config(
    api_key_override: str | None = None,
    provider_id: str | None = None,
    base_url_override: str | None = None,
    model_override: str | None = None,
) -> LlmConfig:
    override = (api_key_override or "").strip()
    server_key = settings.resolve_llm_api_key()
    api_key = override or server_key
    if not api_key:
        raise ValueError("LLM API key is not configured")

    key_source = "client" if override else "server"

    if override:
        resolved_id, base_url, model = resolve_client_llm_endpoint(
            provider_id,
            base_url_override=base_url_override,
            model_override=model_override,
        )
    else:
        resolved_id = DEFAULT_PROVIDER_ID
        base_url = settings.llm_base_url.rstrip("/")
        model = settings.llm_model

    return LlmConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        provider_id=resolved_id,
        key_source=key_source,
    )


def get_ai_status(
    api_key_override: str | None = None,
    provider_id: str | None = None,
    base_url_override: str | None = None,
    model_override: str | None = None,
) -> dict[str, str | bool]:
    server_configured = is_llm_configured()
    client_configured = bool((api_key_override or "").strip())
    configured = is_llm_configured(api_key_override)

    if configured:
        try:
            config = resolve_llm_config(
                api_key_override,
                provider_id=provider_id,
                base_url_override=base_url_override,
                model_override=model_override,
            )
        except ValueError as exc:
            return {
                "ready": False,
                "server_configured": server_configured,
                "client_configured": client_configured,
                "provider": provider_id or DEFAULT_PROVIDER_ID,
                "model": "",
                "detail": str(exc),
            }

        provider = get_llm_provider(config.provider_id)
        provider_name = provider.name if provider else config.provider_id
        detail = (
            f"LLM ready ({provider_name}, your API key)"
            if config.key_source == "client"
            else f"LLM ready ({provider_name}, server configuration)"
        )
        return {
            "ready": True,
            "server_configured": server_configured,
            "client_configured": client_configured,
            "provider": config.provider_id,
            "model": config.model,
            "detail": detail,
        }

    return {
        "ready": False,
        "server_configured": server_configured,
        "client_configured": client_configured,
        "provider": provider_id or DEFAULT_PROVIDER_ID,
        "model": "",
        "detail": "Set FRENCH_READER_LLM_API_KEY in .env or choose a provider and paste your API key in Settings",
    }


def get_llm_providers_payload() -> dict:
    return {
        "default_provider": DEFAULT_PROVIDER_ID,
        "providers": [
            {
                "id": item.id,
                "name": item.name,
                "base_url": item.base_url,
                "default_model": item.default_model,
                "key_hint": item.key_hint,
                "docs_url": item.docs_url,
                "api_style": item.api_style,
                "requires_endpoint": item.requires_endpoint,
                "group": item.group,
            }
            for item in list_llm_providers()
        ],
    }
