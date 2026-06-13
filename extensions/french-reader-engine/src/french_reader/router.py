import logging

from fastapi import APIRouter, HTTPException

from french_reader.ocr_availability import any_ocr_engine_ready, get_ocr_engine_status
from french_reader.ocr_service import recognize_french
from french_reader.schemas import OcrLine, OcrRegionRequest, OcrRegionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/french-reader", tags=["French Reader"])


@router.get("/status")
async def status() -> dict[str, str | bool]:
    return {
        "module": "french-reader",
        "version": "0.2.1",
        "phase": "M2-ocr",
        "ocr_ready": any_ocr_engine_ready(),
    }


@router.get("/ocr/engines")
async def ocr_engines() -> dict[str, object]:
    engines = get_ocr_engine_status()
    return {
        "ready": any_ocr_engine_ready(),
        "engines": [
            {"name": e.name, "available": e.available, "detail": e.detail}
            for e in engines
        ],
    }


@router.post("/ocr/region", response_model=OcrRegionResponse)
async def ocr_region(body: OcrRegionRequest) -> OcrRegionResponse:
    try:
        result = recognize_french(body.image_base64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("OCR failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return OcrRegionResponse(
        text=result.text,
        confidence=round(result.confidence, 4),
        lines=[OcrLine(text=line, confidence=round(conf, 4)) for line, conf in result.lines],
    )
