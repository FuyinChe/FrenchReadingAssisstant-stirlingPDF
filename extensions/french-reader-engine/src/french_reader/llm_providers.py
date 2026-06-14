from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmProviderSpec:
    id: str
    name: str
    base_url: str
    default_model: str
    key_hint: str = ""
    docs_url: str = ""
    api_style: str = "openai"
    requires_endpoint: bool = False
    group: str = "other"


DEFAULT_PROVIDER_ID = "kimi"

_LLM_PROVIDERS: tuple[LlmProviderSpec, ...] = (
    LlmProviderSpec(
        id="kimi",
        name="Kimi (Moonshot)",
        base_url="https://api.moonshot.ai/v1",
        default_model="moonshot-v1-32k",
        key_hint="Moonshot international API key",
        docs_url="https://platform.moonshot.ai/",
        group="recommended",
    ),
    LlmProviderSpec(
        id="openai",
        name="OpenAI",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
        key_hint="OpenAI API key",
        docs_url="https://platform.openai.com/api-keys",
        group="international",
    ),
    LlmProviderSpec(
        id="gemini",
        name="Google Gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        default_model="gemini-2.0-flash",
        key_hint="Google AI Studio API key",
        docs_url="https://aistudio.google.com/apikey",
        group="international",
    ),
    LlmProviderSpec(
        id="claude",
        name="Anthropic Claude",
        base_url="https://api.anthropic.com",
        default_model="claude-3-5-sonnet-latest",
        key_hint="Anthropic API key",
        docs_url="https://console.anthropic.com/settings/keys",
        api_style="anthropic",
        group="international",
    ),
    LlmProviderSpec(
        id="copilot",
        name="Microsoft Copilot (Azure OpenAI)",
        base_url="",
        default_model="",
        key_hint="Azure OpenAI API key",
        docs_url="https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI",
        api_style="azure_openai",
        requires_endpoint=True,
        group="international",
    ),
    LlmProviderSpec(
        id="kimi-cn",
        name="Kimi 国内版",
        base_url="https://api.moonshot.cn/v1",
        default_model="moonshot-v1-32k",
        key_hint="Moonshot China API key",
        docs_url="https://platform.moonshot.cn/",
        group="other",
    ),
    LlmProviderSpec(
        id="deepseek",
        name="DeepSeek",
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
        key_hint="DeepSeek API key",
        docs_url="https://platform.deepseek.com/",
        group="other",
    ),
    LlmProviderSpec(
        id="zhipu",
        name="智谱 AI (GLM)",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        default_model="glm-4-flash",
        key_hint="Zhipu API key",
        docs_url="https://open.bigmodel.cn/",
        group="other",
    ),
    LlmProviderSpec(
        id="openrouter",
        name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        default_model="openai/gpt-4o-mini",
        key_hint="OpenRouter API key",
        docs_url="https://openrouter.ai/keys",
        group="other",
    ),
    LlmProviderSpec(
        id="custom",
        name="Custom (OpenAI-compatible)",
        base_url="",
        default_model="",
        key_hint="API key for your custom endpoint",
        docs_url="",
        requires_endpoint=True,
        group="other",
    ),
)

PROVIDERS: dict[str, LlmProviderSpec] = {item.id: item for item in _LLM_PROVIDERS}


def list_llm_providers() -> list[LlmProviderSpec]:
    return list(_LLM_PROVIDERS)


def get_llm_provider(provider_id: str | None) -> LlmProviderSpec | None:
    cleaned = (provider_id or "").strip()
    if cleaned and cleaned in PROVIDERS:
        return PROVIDERS[cleaned]
    return PROVIDERS.get(DEFAULT_PROVIDER_ID)


def resolve_client_llm_endpoint(
    provider_id: str | None,
    *,
    base_url_override: str | None = None,
    model_override: str | None = None,
) -> tuple[str, str, str]:
    """Return (provider_id, base_url, model) for a client-supplied API key."""
    provider = get_llm_provider(provider_id)
    if provider is None:
        raise ValueError(f"Unknown LLM provider: {provider_id}")

    if provider.requires_endpoint:
        base_url = (base_url_override or "").strip().rstrip("/")
        model = (model_override or "").strip()
        if not base_url or not model:
            label = provider.name
            if provider.id == "copilot":
                raise ValueError(
                    "Azure OpenAI requires endpoint URL and deployment name"
                )
            raise ValueError(f"{label} requires base_url and model")
        return provider.id, base_url, model

    return provider.id, provider.base_url.rstrip("/"), provider.default_model


def get_provider_api_style(provider_id: str) -> str:
    provider = get_llm_provider(provider_id)
    return provider.api_style if provider else "openai"
