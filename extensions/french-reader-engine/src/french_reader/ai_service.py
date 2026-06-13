from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from french_reader.ai_availability import is_llm_configured, resolve_llm_config
from french_reader.config import settings
from french_reader.prompts.templates import ExplainMode, build_messages

logger = logging.getLogger(__name__)


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


async def stream_explain(
    text: str,
    mode: ExplainMode,
    target_lang: str = "zh",
    api_key: str | None = None,
) -> AsyncIterator[str]:
    ensure_llm_ready(api_key)
    cleaned = validate_ai_text(text)
    messages = build_messages(cleaned, mode, target_lang)
    llm = resolve_llm_config(api_key)

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

    try:
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
    except httpx.HTTPError as exc:
        logger.exception("LLM HTTP error")
        raise AiRequestError(str(exc)) from exc
