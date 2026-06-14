from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from french_reader.config import settings
from french_reader.main import app
from french_reader.prompts.templates import build_messages

client = TestClient(app)


def test_build_translate_messages():
    messages = build_messages("Bonjour!", "translate", "zh")
    assert messages[0]["role"] == "system"
    assert "Simplified Chinese" in messages[1]["content"]
    assert "Bonjour!" in messages[1]["content"]


def test_build_vocabulary_messages_include_ipa():
    messages = build_messages("Ils sont bizarres.", "vocabulary", "zh")
    assert messages[0]["role"] == "system"
    assert "IPA" in messages[0]["content"]
    assert "/ipa/" in messages[0]["content"]
    assert "bizarres" in messages[1]["content"]
    assert "Simplified Chinese" in messages[1]["content"] or "zh" in messages[1]["content"].lower()


def test_ai_providers_list():
    response = client.get("/french-reader/ai/providers")
    assert response.status_code == 200
    body = response.json()
    assert body["default_provider"] == "kimi"
    ids = {item["id"] for item in body["providers"]}
    assert "kimi" in ids
    assert "openai" in ids
    assert "gemini" in ids
    assert "claude" in ids
    assert "copilot" in ids
    assert "custom" in ids


def test_resolve_llm_config_uses_provider_for_client_key():
    from french_reader.ai_availability import resolve_llm_config

    config = resolve_llm_config(
        "sk-test",
        provider_id="deepseek",
    )
    assert config.provider_id == "deepseek"
    assert config.base_url == "https://api.deepseek.com/v1"
    assert config.model == "deepseek-chat"
    assert config.key_source == "client"


def test_resolve_llm_config_custom_provider_requires_endpoint():
    from french_reader.ai_availability import resolve_llm_config

    with pytest.raises(ValueError, match="requires base_url and model"):
        resolve_llm_config("sk-test", provider_id="custom")

    config = resolve_llm_config(
        "sk-test",
        provider_id="custom",
        base_url_override="https://example.com/v1",
        model_override="demo-model",
    )
    assert config.base_url == "https://example.com/v1"
    assert config.model == "demo-model"


def test_resolve_llm_config_copilot_requires_azure_fields():
    from french_reader.ai_availability import resolve_llm_config

    with pytest.raises(ValueError, match="Azure OpenAI"):
        resolve_llm_config("sk-test", provider_id="copilot")

    config = resolve_llm_config(
        "sk-test",
        provider_id="copilot",
        base_url_override="https://demo.openai.azure.com",
        model_override="gpt-4o-mini",
    )
    assert config.provider_id == "copilot"
    assert config.base_url == "https://demo.openai.azure.com"
    assert config.model == "gpt-4o-mini"


def test_resolve_llm_config_gemini():
    from french_reader.ai_availability import resolve_llm_config

    config = resolve_llm_config("sk-test", provider_id="gemini")
    assert config.provider_id == "gemini"
    assert "generativelanguage.googleapis.com" in config.base_url
    assert config.model == "gemini-2.0-flash"


def test_ai_status_when_not_configured():
    with patch("french_reader.router.is_llm_configured", return_value=False):
        response = client.get("/french-reader/ai/status")
    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is False
    assert "LLM" in body["detail"]


def test_ai_explain_requires_llm():
    with patch("french_reader.router.is_llm_configured", return_value=False):
        response = client.post(
            "/french-reader/ai/explain",
            json={"text": "Bonjour", "mode": "translate", "target_lang": "zh"},
        )
    assert response.status_code == 503


@patch("french_reader.router.is_llm_configured", return_value=True)
@patch("french_reader.router.stream_explain")
def test_ai_explain_accepts_client_api_key(mock_stream, _configured):
    async def fake_stream(*_args, **_kwargs):
        yield "你好"

    mock_stream.side_effect = fake_stream

    response = client.post(
        "/french-reader/ai/explain",
        json={
            "text": "Bonjour",
            "mode": "translate",
            "target_lang": "zh",
            "api_key": "sk-user-test-key",
        },
    )
    assert response.status_code == 200
    mock_stream.assert_called_once()
    assert mock_stream.call_args.kwargs["provider_id"] is None


@patch("french_reader.router.is_llm_configured", return_value=True)
@patch("french_reader.router.stream_explain")
def test_ai_explain_accepts_provider(mock_stream, _configured):
    async def fake_stream(*_args, **_kwargs):
        yield "你好"

    mock_stream.side_effect = fake_stream

    response = client.post(
        "/french-reader/ai/explain",
        json={
            "text": "Bonjour",
            "mode": "translate",
            "target_lang": "zh",
            "api_key": "sk-user-test-key",
            "provider": "openai",
        },
    )
    assert response.status_code == 200
    assert mock_stream.call_args.kwargs["provider_id"] == "openai"


def test_ai_status_with_client_api_key():
    with patch("french_reader.router.is_llm_configured", side_effect=lambda key=None: bool(key)):
        response = client.get(
            "/french-reader/ai/status",
            params={"api_key": "sk-user-test-key"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is True
    assert body["client_configured"] is True


@patch("french_reader.router.is_llm_configured", return_value=True)
@patch("french_reader.router.stream_explain")
def test_ai_explain_sse(mock_stream, _configured):
    async def fake_stream(*_args, **_kwargs):
        yield "你好"
        yield "，世界"

    mock_stream.side_effect = fake_stream

    with client.stream(
        "POST",
        "/french-reader/ai/explain",
        json={"text": "Bonjour le monde", "mode": "translate", "target_lang": "zh"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = "".join(response.iter_text())

    assert '"delta": "你好"' in body or '"delta":"你好"' in body
    assert "[DONE]" in body


def test_ai_explain_rejects_empty_text():
    response = client.post(
        "/french-reader/ai/explain",
        json={"text": "   ", "mode": "translate"},
    )
    assert response.status_code == 400


def test_validate_ai_text_length():
    from french_reader.ai_service import validate_ai_text

    with pytest.raises(ValueError, match="exceeds"):
        validate_ai_text("a" * (settings.ai_max_chars + 1))
