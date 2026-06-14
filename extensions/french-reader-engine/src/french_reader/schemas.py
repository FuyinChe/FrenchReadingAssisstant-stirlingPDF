from typing import Literal

from pydantic import BaseModel, Field, model_validator

_AI_MODES = frozenset({"translate", "vocabulary", "grammar"})


class BBox(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    w: float = Field(gt=0, le=1)
    h: float = Field(gt=0, le=1)


class OcrRegionRequest(BaseModel):
    image_base64: str = Field(min_length=16)
    page: int = Field(ge=1)
    bbox: BBox
    lang: str = "fr"


class OcrLine(BaseModel):
    text: str
    confidence: float = Field(ge=0, le=1)


class OcrRegionResponse(BaseModel):
    text: str
    confidence: float = Field(ge=0, le=1)
    lines: list[OcrLine] = Field(default_factory=list)


class TtsVoice(BaseModel):
    id: str
    name: str
    locale: str
    gender: str


class TtsVoicesResponse(BaseModel):
    voices: list[TtsVoice]
    default_voice: str


class TtsSynthesizeRequest(BaseModel):
    text: str = Field(min_length=1)
    voice: str = "fr-FR-DeniseNeural"
    rate: str = "+0%"


AiExplainMode = Literal["translate", "vocabulary", "grammar"]


class AiExplainRequest(BaseModel):
    text: str = Field(min_length=1)
    mode: AiExplainMode = "translate"
    target_lang: str = Field(default="zh", min_length=2, max_length=8)
    api_key: str | None = Field(default=None, max_length=512)
    provider: str | None = Field(default=None, max_length=32)
    base_url: str | None = Field(default=None, max_length=256)
    model: str | None = Field(default=None, max_length=128)


class LlmProviderInfo(BaseModel):
    id: str
    name: str
    base_url: str
    default_model: str
    key_hint: str = ""
    docs_url: str = ""
    api_style: str = "openai"
    requires_endpoint: bool = False
    group: str = "other"


class LlmProvidersResponse(BaseModel):
    default_provider: str
    providers: list[LlmProviderInfo]


class AiStatusResponse(BaseModel):
    ready: bool
    server_configured: bool = False
    client_configured: bool = False
    provider: str
    model: str
    detail: str


class HistoryExportEntry(BaseModel):
    id: str
    created_at: str
    file_name: str
    page: int = Field(ge=1)
    text: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    translations: dict[AiExplainMode, str] | None = None
    translation: str | None = None
    translation_mode: AiExplainMode | None = None


class HistoryExportRequest(BaseModel):
    source_file_name: str = Field(min_length=1)
    entries: list[HistoryExportEntry] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        source = str(data.get("source_file_name") or "").strip() or "notes"
        cleaned_entries: list[dict] = []

        for raw in data.get("entries") or []:
            if not isinstance(raw, dict):
                continue

            text = str(raw.get("text") or "").strip()
            if not text:
                continue

            try:
                confidence = float(raw.get("confidence", 0))
            except (TypeError, ValueError):
                confidence = 0.0
            if confidence > 1.0:
                confidence /= 100.0
            confidence = min(1.0, max(0.0, confidence))

            translations = raw.get("translations")
            if isinstance(translations, dict):
                translations = {
                    key: str(value).strip()
                    for key, value in translations.items()
                    if key in _AI_MODES and str(value).strip()
                } or None
            else:
                translations = None

            translation_mode = raw.get("translation_mode")
            if translation_mode not in _AI_MODES:
                translation_mode = None

            translation = raw.get("translation")
            if translation is not None:
                translation = str(translation).strip() or None

            try:
                page = max(1, int(raw.get("page", 1)))
            except (TypeError, ValueError):
                page = 1

            cleaned_entries.append(
                {
                    **raw,
                    "text": text,
                    "confidence": confidence,
                    "translations": translations,
                    "translation_mode": translation_mode,
                    "translation": translation,
                    "page": page,
                    "file_name": str(raw.get("file_name") or "document"),
                }
            )

        if not cleaned_entries:
            raise ValueError("No history entries with recognized text to export")

        return {"source_file_name": source, "entries": cleaned_entries}


class AutoBubblesRequest(BaseModel):
    image_base64: str = Field(min_length=16)
    page: int = Field(ge=1)
    confidence_threshold: float = Field(default=0.35, ge=0.05, le=0.95)
    preprocess: bool = False
    prefer_yolo: bool = True


class DetectedBubble(BaseModel):
    bbox: BBox
    confidence: float = Field(ge=0, le=1)
    detector: str


class AutoBubblesResponse(BaseModel):
    page: int = Field(ge=1)
    bubbles: list[DetectedBubble] = Field(default_factory=list)
    detector: str
    preprocess: bool = False


class AutoParagraphsRequest(BaseModel):
    image_base64: str = Field(min_length=16)
    page: int = Field(ge=1)
    confidence_threshold: float = Field(default=0.35, ge=0.05, le=0.95)
    preprocess: bool = False


class DetectedParagraph(BaseModel):
    bbox: BBox
    confidence: float = Field(ge=0, le=1)
    detector: str
    order: int = Field(ge=1)


class AutoParagraphsResponse(BaseModel):
    page: int = Field(ge=1)
    paragraphs: list[DetectedParagraph] = Field(default_factory=list)
    detector: str
    preprocess: bool = False
