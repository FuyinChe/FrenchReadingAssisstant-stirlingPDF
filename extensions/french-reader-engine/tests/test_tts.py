from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from french_reader.config import settings
from french_reader.main import app
from french_reader.tts_service import TtsVoice, validate_tts_text

client = TestClient(app)


def test_validate_tts_text_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_tts_text("   ")


def test_validate_tts_text_rejects_long_text():
    with pytest.raises(ValueError, match="exceeds"):
        validate_tts_text("a" * (settings.tts_max_chars + 1))


@patch("french_reader.router.list_voices", new_callable=AsyncMock)
def test_tts_voices_endpoint(mock_list_voices):
    mock_list_voices.return_value = [
        TtsVoice(
            id="fr-FR-DeniseNeural",
            name="Microsoft Denise Online (Natural) - French (France)",
            locale="fr-FR",
            gender="Female",
        ),
        TtsVoice(
            id="fr-FR-HenriNeural",
            name="Microsoft Henri Online (Natural) - French (France)",
            locale="fr-FR",
            gender="Male",
        ),
    ]

    response = client.get("/french-reader/tts/voices?lang=fr")
    assert response.status_code == 200
    body = response.json()
    assert body["default_voice"] == "fr-FR-DeniseNeural"
    assert len(body["voices"]) == 2
    assert body["voices"][0]["id"] == "fr-FR-DeniseNeural"


@patch("french_reader.router.synthesize_speech", new_callable=AsyncMock)
def test_tts_synthesize_streams_audio(mock_synthesize):
    mock_synthesize.return_value = b"fake-audio-chunk"

    response = client.post(
        "/french-reader/tts/synthesize",
        json={
            "text": "Bonjour le monde.",
            "voice": "fr-FR-DeniseNeural",
            "rate": "+0%",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/mpeg")
    assert response.content == b"fake-audio-chunk"


def test_tts_synthesize_rejects_invalid_rate():
    response = client.post(
        "/french-reader/tts/synthesize",
        json={
            "text": "Bonjour",
            "voice": "fr-FR-DeniseNeural",
            "rate": "fast",
        },
    )
    assert response.status_code == 400


def test_tts_synthesize_rejects_empty_text():
    response = client.post(
        "/french-reader/tts/synthesize",
        json={
            "text": "   ",
            "voice": "fr-FR-DeniseNeural",
        },
    )
    assert response.status_code == 400
