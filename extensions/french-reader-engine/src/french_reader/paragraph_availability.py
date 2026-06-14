from __future__ import annotations

from dataclasses import dataclass

from french_reader.bubble_availability import _opencv_available


@dataclass
class ParagraphDetectorStatus:
    opencv_available: bool
    ready: bool
    detail: str


def get_paragraph_detector_status() -> ParagraphDetectorStatus:
    opencv_ok, opencv_detail = _opencv_available()
    tess_ok = False
    tess_detail = "Tesseract not installed — paragraph detect uses OpenCV only"
    try:
        from french_reader.paragraph_tesseract import tesseract_layout_available

        if tesseract_layout_available():
            tess_ok = True
            tess_detail = "Tesseract layout available for higher-accuracy paragraph boxes"
    except Exception as exc:
        tess_detail = str(exc)

    detail = f"opencv={opencv_detail}; tesseract={tess_detail}"
    return ParagraphDetectorStatus(
        opencv_available=opencv_ok,
        ready=opencv_ok,
        detail=detail if opencv_ok else opencv_detail,
    )
