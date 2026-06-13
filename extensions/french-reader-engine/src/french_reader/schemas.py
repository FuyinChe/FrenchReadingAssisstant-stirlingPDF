from typing import Literal

from pydantic import BaseModel, Field


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
