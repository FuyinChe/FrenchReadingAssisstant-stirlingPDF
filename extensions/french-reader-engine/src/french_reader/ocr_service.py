from __future__ import annotations

import base64
import io
import logging
import sys
from dataclasses import dataclass

from PIL import Image

from french_reader.ocr_availability import format_setup_hint
from french_reader.text_postprocess import extract_tts_lines, postprocess_french_text

logger = logging.getLogger(__name__)

_paddle_ocr = None


@dataclass
class OcrRecognition:
    text: str
    confidence: float
    lines: list[tuple[str, float]]


def _decode_image(image_base64: str) -> Image.Image:
    raw = image_base64.strip()
    if "," in raw:
        raw = raw.split(",", 1)[1]
    data = base64.b64decode(raw)
    image = Image.open(io.BytesIO(data))
    return image.convert("RGB")


def _get_paddle_ocr():
    global _paddle_ocr
    if _paddle_ocr is None:
        from paddleocr import PaddleOCR

        _paddle_ocr = PaddleOCR(use_angle_cls=True, lang="fr", show_log=False)
    return _paddle_ocr


def _recognize_paddle(image: Image.Image) -> OcrRecognition | None:
    try:
        import numpy as np

        ocr = _get_paddle_ocr()
        result = ocr.ocr(np.array(image), cls=True)
    except Exception as exc:
        logger.warning("PaddleOCR unavailable: %s", exc)
        return None

    lines: list[tuple[str, float]] = []
    for block in result or []:
        for item in block or []:
            if not item or len(item) < 2:
                continue
            text = str(item[1][0]).strip()
            conf = float(item[1][1])
            if text:
                lines.append((text, conf))

    if not lines:
        return OcrRecognition(text="", confidence=0.0, lines=[])

    text = postprocess_french_text("\n".join(line for line, _ in lines))
    confidence = sum(c for _, c in lines) / len(lines)
    tts_lines = extract_tts_lines(text)
    line_results = (
        [(line, confidence) for line in tts_lines]
        if tts_lines
        else lines
    )
    return OcrRecognition(text=text, confidence=confidence, lines=line_results)


def _assemble_tesseract_lines(data: dict) -> list[tuple[str, float]]:
    """Group Tesseract word boxes into reading-order lines."""
    from collections import defaultdict

    buckets: dict[tuple[int, int, int], list[tuple[int, str, float]]] = defaultdict(list)
    texts = data.get("text", [])
    for i in range(len(texts)):
        text = (texts[i] or "").strip()
        if not text:
            continue
        conf = float(data["conf"][i])
        if conf < 0:
            continue
        key = (
            int(data["block_num"][i]),
            int(data["par_num"][i]),
            int(data["line_num"][i]),
        )
        buckets[key].append((int(data["word_num"][i]), text, conf / 100.0))

    assembled: list[tuple[str, float, tuple[int, int]]] = []
    for (block, par, _line), words in sorted(buckets.items()):
        words.sort(key=lambda item: item[0])
        line_text = " ".join(word for _, word, _ in words)
        avg_conf = sum(conf for _, _, conf in words) / len(words)
        assembled.append((line_text, avg_conf, (block, par)))

    lines: list[tuple[str, float]] = []
    for line_text, avg_conf, _par_key in assembled:
        lines.append((line_text, avg_conf))
    return lines


def _tesseract_lang_candidates() -> list[str]:
    import subprocess

    try:
        out = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        langs = {
            line.strip()
            for line in out.stdout.splitlines()
            if line.strip() and not line.startswith("List of")
        }
    except (FileNotFoundError, subprocess.SubprocessError):
        return ["fra", "eng"]

    ordered: list[str] = []
    for candidate in ("fra", "fr", "eng"):
        if candidate in langs and candidate not in ordered:
            ordered.append(candidate)
    return ordered or ["fra", "eng"]


def _recognize_tesseract(image: Image.Image) -> OcrRecognition | None:
    try:
        import pytesseract
    except ImportError:
        logger.warning("pytesseract not installed")
        return None

    last_error: Exception | None = None
    for lang in _tesseract_lang_candidates():
        try:
            data = pytesseract.image_to_data(
                image,
                lang=lang,
                output_type=pytesseract.Output.DICT,
            )
        except Exception as exc:
            last_error = exc
            logger.warning("Tesseract lang=%s failed: %s", lang, exc)
            continue

        lines = _assemble_tesseract_lines(data)
        content_lines = [(line, conf) for line, conf in lines if line]

        if not content_lines:
            return OcrRecognition(text="", confidence=0.0, lines=[])

        text = postprocess_french_text("\n".join(line for line, _ in lines))
        confidence = sum(conf for _, conf in content_lines) / len(content_lines)
        tts_lines = extract_tts_lines(text)
        line_results = (
            [(line, confidence) for line in tts_lines]
            if tts_lines
            else content_lines
        )
        return OcrRecognition(
            text=text,
            confidence=confidence,
            lines=line_results,
        )

    if last_error:
        logger.warning("All Tesseract languages failed: %s", last_error)
    return None


def _engine_order() -> list:
    # Tesseract is lighter and more reliable on macOS dev machines.
    if sys.platform == "darwin":
        return [_recognize_tesseract, _recognize_paddle]
    return [_recognize_paddle, _recognize_tesseract]


def recognize_french(image_base64: str) -> OcrRecognition:
    image = _decode_image(image_base64)

    for recognize in _engine_order():
        result = recognize(image)
        if result is not None:
            return result

    raise RuntimeError(format_setup_hint())
