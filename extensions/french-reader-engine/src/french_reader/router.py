import json
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse

from french_reader.ai_availability import get_ai_status, is_llm_configured
from french_reader.bubble_availability import get_bubble_detector_status
from french_reader.bubble_detector import detect_speech_bubbles
from french_reader.ai_service import (
    AiConfigurationError,
    AiRequestError,
    stream_explain,
    validate_ai_text,
)
from french_reader.config import settings
from french_reader.ocr_availability import any_ocr_engine_ready, get_ocr_engine_status
from french_reader.ocr_service import recognize_french
from french_reader.export_service import build_history_pdf
from french_reader.schemas import (
    AiExplainRequest,
    AiStatusResponse,
    AutoBubblesRequest,
    AutoBubblesResponse,
    DetectedBubble,
    HistoryExportRequest,
    OcrLine,
    OcrRegionRequest,
    OcrRegionResponse,
    TtsSynthesizeRequest,
    TtsVoice,
    TtsVoicesResponse,
)
from french_reader.tts_service import (
    default_voice_for_lang,
    list_voices,
    normalize_rate,
    synthesize_speech,
    validate_tts_text,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/french-reader", tags=["French Reader"])


@router.get("/status")
async def status() -> dict[str, str | bool]:
    return {
        "module": "french-reader",
        "version": "0.4.0",
        "phase": "M5-bubbles",
        "ocr_ready": any_ocr_engine_ready(),
        "bubble_ready": get_bubble_detector_status().ready,
        "tts_ready": True,
        "ai_ready": is_llm_configured(),
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


@router.get("/ocr/bubbles/status")
async def bubble_detector_status() -> dict[str, object]:
    status = get_bubble_detector_status()
    return {
        "ready": status.ready,
        "opencv_available": status.opencv_available,
        "yolo_available": status.yolo_available,
        "detail": status.detail,
        "default_model": settings.bubble_yolo_model,
    }


@router.post("/ocr/auto-bubbles", response_model=AutoBubblesResponse)
async def ocr_auto_bubbles(body: AutoBubblesRequest) -> AutoBubblesResponse:
    bubble_status = get_bubble_detector_status()
    if not bubble_status.ready:
        raise HTTPException(
            status_code=503,
            detail=(
                "Bubble detection is not configured. Run:\n"
                "  cd extensions/french-reader-engine && uv sync --extra bubble"
            ),
        )

    threshold = body.confidence_threshold or settings.bubble_confidence_threshold
    try:
        detections, detector = detect_speech_bubbles(
            body.image_base64,
            confidence_threshold=threshold,
            preprocess=body.preprocess,
            prefer_yolo=body.prefer_yolo,
            yolo_model_path=settings.bubble_yolo_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Bubble detection failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AutoBubblesResponse(
        page=body.page,
        detector=detector,
        preprocess=body.preprocess,
        bubbles=[
            DetectedBubble(
                bbox=item.bbox,
                confidence=round(item.confidence, 4),
                detector=item.detector,
            )
            for item in detections
        ],
    )


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


@router.get("/tts/voices", response_model=TtsVoicesResponse)
async def tts_voices(lang: str = Query(default="fr", min_length=2, max_length=8)) -> TtsVoicesResponse:
    try:
        voices = await list_voices(lang)
    except Exception as exc:
        logger.exception("Failed to list TTS voices")
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not voices:
        raise HTTPException(status_code=404, detail=f"No TTS voices found for lang={lang}")

    default_voice = settings.tts_default_voice or default_voice_for_lang(lang)
    if not any(voice.id == default_voice for voice in voices):
        default_voice = voices[0].id

    return TtsVoicesResponse(
        voices=[
            TtsVoice(
                id=voice.id,
                name=voice.name,
                locale=voice.locale,
                gender=voice.gender,
            )
            for voice in voices
        ],
        default_voice=default_voice,
    )


@router.post("/tts/synthesize")
async def tts_synthesize(body: TtsSynthesizeRequest) -> Response:
    try:
        validate_tts_text(body.text)
        normalize_rate(body.rate)
        audio = await synthesize_speech(body.text, body.voice, body.rate)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return Response(content=audio, media_type="audio/mpeg")


@router.get("/ai/status", response_model=AiStatusResponse)
async def ai_status(
    api_key: str | None = Query(default=None, max_length=512),
) -> AiStatusResponse:
    status = get_ai_status(api_key)
    return AiStatusResponse(**status)


@router.post("/ai/explain")
async def ai_explain(body: AiExplainRequest) -> StreamingResponse:
    try:
        validate_ai_text(body.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not is_llm_configured(body.api_key):
        raise HTTPException(
            status_code=503,
            detail="LLM is not configured. Set FRENCH_READER_LLM_API_KEY or paste your API key in Settings.",
        )

    async def event_stream():
        try:
            async for delta in stream_explain(body.text, body.mode, body.target_lang, body.api_key):
                payload = json.dumps({"delta": delta}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except AiConfigurationError as exc:
            payload = json.dumps({"error": str(exc)}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        except AiRequestError as exc:
            logger.warning("AI explain failed: %s", exc)
            payload = json.dumps({"error": str(exc)}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        except Exception as exc:
            logger.exception("AI explain failed")
            payload = json.dumps({"error": str(exc)}, ensure_ascii=False)
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/export/pdf")
async def export_history_pdf(body: HistoryExportRequest) -> Response:
    try:
        pdf_bytes = build_history_pdf(body.entries, body.source_file_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("PDF export failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    safe_name = "".join(
        char if char.isalnum() or char in "._-" else "_"
        for char in body.source_file_name
    ) or "notes"
    filename = f"french-reader-{safe_name}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
