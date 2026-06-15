from __future__ import annotations

import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass

from french_reader.config import settings

logger = logging.getLogger(__name__)

_RATE_PATTERN = re.compile(r"^[+-]\d{1,3}%$")
_DEFAULT_FR_VOICE = "fr-FR-DeniseNeural"


@dataclass(frozen=True)
class TtsVoice:
    id: str
    name: str
    locale: str
    gender: str


def normalize_rate(rate: str) -> str:
    cleaned = rate.strip()
    if not _RATE_PATTERN.match(cleaned):
        raise ValueError('Rate must look like "+0%" or "-10%"')
    return cleaned


def validate_tts_text(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Text is empty")
    if len(cleaned) > settings.tts_max_chars:
        raise ValueError(
            f"Text exceeds {settings.tts_max_chars} characters "
            f"({len(cleaned)} given)"
        )
    return cleaned


def default_voice_for_lang(lang: str) -> str:
    prefix = lang.lower().split("-")[0]
    if prefix == "fr":
        return _DEFAULT_FR_VOICE
    return _DEFAULT_FR_VOICE


async def list_voices(lang: str = "fr") -> list[TtsVoice]:
    import edge_tts

    prefix = lang.lower().split("-")[0]
    raw_voices = await edge_tts.list_voices()
    filtered = [
        voice
        for voice in raw_voices
        if voice.get("Locale", "").lower().startswith(prefix)
    ]
    filtered.sort(key=lambda voice: (voice.get("Locale", ""), voice.get("ShortName", "")))

    return [
        TtsVoice(
            id=voice["ShortName"],
            name=voice.get("FriendlyName", voice["ShortName"]),
            locale=voice.get("Locale", ""),
            gender=voice.get("Gender", ""),
        )
        for voice in filtered
    ]


async def stream_speech(text: str, voice: str, rate: str = "+0%") -> AsyncIterator[bytes]:
    import edge_tts

    cleaned = validate_tts_text(text)
    normalized_rate = normalize_rate(rate)
    communicate = edge_tts.Communicate(cleaned, voice, rate=normalized_rate)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


async def synthesize_speech(text: str, voice: str, rate: str = "+0%") -> bytes:
    chunks = [part async for part in stream_speech(text, voice, rate)]
    if not chunks:
        raise RuntimeError("TTS produced no audio")
    return b"".join(chunks)
