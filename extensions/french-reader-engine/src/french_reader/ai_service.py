from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from french_reader.ai_availability import is_llm_configured, resolve_llm_config
from french_reader.config import settings
from french_reader.llm_providers import get_provider_api_style
from french_reader.prompts.templates import ExplainMode, build_messages

logger = logging.getLogger(__name__)

_AZURE_API_VERSION = "2024-08-01-preview"
_ANTHROPIC_VERSION = "2023-06-01"


class AiConfigurationError(RuntimeError):
    pass


class AiRequestError(RuntimeError):
    pass


def validate_ai_text(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Text is empty")
    if len(cleaned) > settings.ai_max_chars:
        raise ValueError(
            f"Text exceeds {settings.ai_max_chars} characters ({len(cleaned)} given)"
        )
    return cleaned


def ensure_llm_ready(api_key: str | None = None) -> None:
    if not is_llm_configured(api_key):
        raise AiConfigurationError(
            "LLM is not configured. Set FRENCH_READER_LLM_API_KEY or paste your API key in Settings."
        )


def _split_messages_for_anthropic(
    messages: list[dict[str, str]],
) -> tuple[str, list[dict[str, str]]]:
    system_parts: list[str] = []
    conversation: list[dict[str, str]] = []
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        if role == "system":
            system_parts.append(content)
        elif role in {"user", "assistant"}:
            conversation.append({"role": role, "content": content})
    return "\n\n".join(system_parts), conversation


async def _stream_openai_compatible(
    *,
    url: str,
    headers: dict[str, str],
    payload: dict,
) -> AsyncIterator[str]:
    async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            if response.status_code >= 400:
                body = await response.aread()
                detail = body.decode("utf-8", errors="replace")
                raise AiRequestError(
                    f"LLM request failed ({response.status_code}): {detail[:500]}"
                )

            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line.removeprefix("data:").strip()
                if not data or data == "[DONE]":
                    continue
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    logger.debug("Skipping non-JSON SSE chunk: %s", data[:120])
                    continue

                if chunk.get("error"):
                    message = chunk["error"].get("message", "LLM stream error")
                    raise AiRequestError(message)

                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield content


async def _stream_anthropic(
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> AsyncIterator[str]:
    system_prompt, conversation = _split_messages_for_anthropic(messages)
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": _ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    payload: dict = {
        "model": model,
        "max_tokens": 4096,
        "messages": conversation,
        "stream": True,
        "temperature": 0.3,
    }
    if system_prompt:
        payload["system"] = system_prompt

    async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            if response.status_code >= 400:
                body = await response.aread()
                detail = body.decode("utf-8", errors="replace")
                raise AiRequestError(
                    f"LLM request failed ({response.status_code}): {detail[:500]}"
                )

            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line.removeprefix("data:").strip()
                if not data or data == "[DONE]":
                    continue
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue

                if chunk.get("type") == "error":
                    raise AiRequestError(chunk.get("error", {}).get("message", "LLM stream error"))

                if chunk.get("type") == "content_block_delta":
                    text = chunk.get("delta", {}).get("text")
                    if text:
                        yield text


async def _stream_azure_openai(
    *,
    endpoint: str,
    deployment: str,
    api_key: str,
    messages: list[dict[str, str]],
) -> AsyncIterator[str]:
    url = (
        f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions"
        f"?api-version={_AZURE_API_VERSION}"
    )
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "messages": messages,
        "stream": True,
        "temperature": 0.3,
    }
    async for chunk in _stream_openai_compatible(url=url, headers=headers, payload=payload):
        yield chunk


async def stream_explain(
    text: str,
    mode: ExplainMode,
    target_lang: str = "zh",
    api_key: str | None = None,
    provider_id: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> AsyncIterator[str]:
    ensure_llm_ready(api_key)
    cleaned = validate_ai_text(text)
    messages = build_messages(cleaned, mode, target_lang)
    llm = resolve_llm_config(
        api_key,
        provider_id=provider_id,
        base_url_override=base_url,
        model_override=model,
    )

    api_style = get_provider_api_style(llm.provider_id)

    try:
        if api_style == "anthropic":
            async for delta in _stream_anthropic(
                api_key=llm.api_key,
                model=llm.model,
                messages=messages,
            ):
                yield delta
            return

        if api_style == "azure_openai":
            async for delta in _stream_azure_openai(
                endpoint=llm.base_url,
                deployment=llm.model,
                api_key=llm.api_key,
                messages=messages,
            ):
                yield delta
            return

        url = f"{llm.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {llm.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": llm.model,
            "messages": messages,
            "stream": True,
            "temperature": 0.3,
        }
        async for delta in _stream_openai_compatible(url=url, headers=headers, payload=payload):
            yield delta
    except httpx.HTTPError as exc:
        logger.exception("LLM HTTP error")
        raise AiRequestError(str(exc)) from exc
