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
