"""Tesseract layout analysis for paragraph region detection."""

from __future__ import annotations

import logging
import shutil
from collections import defaultdict

from PIL import Image

from french_reader.bubble_detector import _normalize_bbox
from french_reader.bubble_detector import BubbleDetection

logger = logging.getLogger(__name__)


def tesseract_layout_available() -> bool:
    if not shutil.which("tesseract"):
        return False
    try:
        import pytesseract  # noqa: F401
    except ImportError:
        return False
    return True


def _tesseract_lang_candidates() -> list[str]:
    from french_reader.ocr_service import _tesseract_lang_candidates

    return _tesseract_lang_candidates()


def _lines_from_tesseract_data(
    data: dict,
    *,
    offset_x: int,
    offset_y: int,
    min_conf: int,
) -> list[tuple[int, int, int, int, float]]:
    buckets: dict[tuple[int, int, int], list[tuple[int, int, int, int, float]]] = defaultdict(list)
    texts = data.get("text", [])
    for index in range(len(texts)):
        text = (texts[index] or "").strip()
        if not text:
            continue
        try:
            conf = float(data["conf"][index])
        except (TypeError, ValueError):
            continue
        if conf < min_conf:
            continue

        key = (
            int(data["block_num"][index]),
            int(data["par_num"][index]),
            int(data["line_num"][index]),
        )
        left = int(data["left"][index]) + offset_x
        top = int(data["top"][index]) + offset_y
        width = int(data["width"][index])
        height = int(data["height"][index])
        if width <= 0 or height <= 0:
            continue
        buckets[key].append((left, top, width, height, conf / 100.0))

    lines: list[tuple[int, int, int, int, float]] = []
    for words in buckets.values():
        xs = [item[0] for item in words]
        ys = [item[1] for item in words]
        x2s = [item[0] + item[2] for item in words]
        y2s = [item[1] + item[3] for item in words]
        avg_conf = sum(item[4] for item in words) / len(words)
        lines.append(
            (
                min(xs),
                min(ys),
                max(x2s) - min(xs),
                max(y2s) - min(ys),
                avg_conf,
            )
        )
    return sorted(lines, key=lambda item: (item[1], item[0]))


def tesseract_lines_in_region(
    image: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    *,
    psm: int = 6,
    min_conf: int = 20,
) -> list[tuple[int, int, int, int, float]] | None:
    if not tesseract_layout_available():
        return None

    import pytesseract

    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(image.width, x1)
    y1 = min(image.height, y1)
    if x1 <= x0 or y1 <= y0:
        return None

    crop = image.crop((x0, y0, x1, y1))
    config = f"--psm {psm} -c preserve_interword_spaces=1"

    for lang in _tesseract_lang_candidates():
        try:
            data = pytesseract.image_to_data(
                crop,
                lang=lang,
                config=config,
                output_type=pytesseract.Output.DICT,
            )
        except Exception as exc:
            logger.debug("Tesseract paragraph layout failed lang=%s: %s", lang, exc)
            continue

        lines = _lines_from_tesseract_data(
            data,
            offset_x=x0,
            offset_y=y0,
            min_conf=min_conf,
        )
        if lines:
            return lines

    return None


def _score_tesseract_group(
    lines,
    img_w: int,
    img_h: int,
    *,
    illustrated: bool,
) -> tuple[tuple[int, int, int, int], float] | None:
    from french_reader.paragraph_detector import _expand_paragraph_bbox, _union_bbox

    if len(lines) < 2:
        if illustrated or not lines:
            return None
        line = lines[0]
        if line.w < max(70, int(img_w * 0.15)):
            return None
        if line.w / max(line.h, 1) < 2.0:
            return None

    x, y, bw, bh = _union_bbox([line.as_tuple() for line in lines])
    x, y, bw, bh = _expand_paragraph_bbox(
        x,
        y,
        bw,
        bh,
        img_w,
        img_h,
        illustrated=illustrated,
    )

    if bw < max(70, int(img_w * (0.12 if illustrated else 0.08))):
        return None
    if bh < max(18, int(img_h * 0.018)):
        return None

    avg_conf = 0.75
    confidence = min(
        0.94,
        0.5
        + min(len(lines), 8) * 0.05
        + min(bw / img_w, 0.55) * 0.18
        + avg_conf * 0.12,
    )
    return (x, y, bw, bh), confidence


def _filter_quality_tesseract_raw_lines(
    raw_lines: list[tuple[int, int, int, int, float]],
    img_w: int,
    img_h: int,
    *,
    min_conf: float = 0.32,
    illustrated: bool = True,
) -> list[tuple[int, int, int, int, float]]:
    min_width_ratio = 0.12 if illustrated else 0.06
    kept: list[tuple[int, int, int, int, float]] = []
    for x, y, w, h, conf in raw_lines:
        aspect = w / max(h, 1)
        if conf < min_conf:
            continue
        if w < img_w * min_width_ratio:
            continue
        if illustrated:
            if aspect < 4.5 and w < img_w * 0.25:
                continue
            if h > img_h * 0.09:
                continue
        else:
            if aspect < 2.0 and w < img_w * 0.12:
                continue
            if h > img_h * 0.12:
                continue
        kept.append((x, y, w, h, conf))
    return kept


def _filter_tesseract_picture_book_lines(lines, img_w: int):
    min_text_width = max(40, int(img_w * 0.08))
    max_text_width = int(img_w * 0.88)
    kept = [line for line in lines if min_text_width <= line.w <= max_text_width]
    if len(kept) < 2:
        return []
    return sorted(kept, key=lambda item: item.y)


def try_detect_picture_book_paragraphs_tesseract(
    image: Image.Image,
    gray,
    img_w: int,
    img_h: int,
    *,
    confidence_threshold: float,
) -> list[BubbleDetection] | None:
    from french_reader.paragraph_detector import (
        _filter_lines_to_primary_cluster,
        _lines_look_like_text_block,
        _score_picture_book_zone,
        _should_use_picture_book_detector,
        _TextLine,
        _expand_paragraph_bbox,
        _union_bbox,
    )

    import numpy as np

    rgb = np.array(image)
    if not _should_use_picture_book_detector(rgb, gray, img_w, img_h):
        return None

    margin_x = max(8, int(img_w * 0.035))
    zones = [
        (margin_x, 0, img_w - margin_x, int(img_h * 0.43)),
        (margin_x, int(img_h * 0.52), img_w - margin_x, img_h),
    ]

    candidates: list[tuple[float, BubbleDetection]] = []
    for x0, y0, x1, y1 in zones:
        raw_lines = tesseract_lines_in_region(image, x0, y0, x1, y1, psm=6, min_conf=15)
        if not raw_lines or len(raw_lines) < 2:
            continue

        raw_lines = _filter_quality_tesseract_raw_lines(raw_lines, img_w, img_h)
        if len(raw_lines) < 2:
            continue

        lines = [_TextLine(x=x, y=y, w=w, h=h) for x, y, w, h, _conf in raw_lines]
        lines = _filter_lines_to_primary_cluster(lines, y0, y1, img_w, img_h)
        lines = _filter_tesseract_picture_book_lines(lines, img_w)
        if not _lines_look_like_text_block(lines, img_w, img_h):
            continue

        zone_score = _score_picture_book_zone(lines, y0, y1, img_w, img_h)
        if zone_score < 3:
            continue

        avg_conf = sum(item[4] for item in raw_lines[: len(lines)]) / max(len(lines), 1)
        ex, ey, ew, eh = _union_bbox([line.as_tuple() for line in lines])
        ex, ey, ew, eh = _expand_paragraph_bbox(ex, ey, ew, eh, img_w, img_h, illustrated=True)

        zone_h = max(1, y1 - y0)
        center_y = (ey + eh / 2) / img_h
        if y0 <= img_h * 0.05 and (ey - y0) / zone_h > 0.72:
            continue
        if y0 >= img_h * 0.5 and (ey + eh - y0) / zone_h < 0.28:
            continue
        if eh / img_h > 0.32:
            continue

        confidence = min(
            0.94,
            0.5 + len(lines) * 0.05 + ew / img_w * 0.12 + zone_score * 0.012 + avg_conf * 0.15,
        )
        if confidence < confidence_threshold:
            continue

        candidates.append(
            (
                zone_score,
                BubbleDetection(
                    bbox=_normalize_bbox(ex, ey, ew, eh, img_w, img_h),
                    confidence=confidence,
                    detector="tesseract-paragraph",
                ),
            ),
        )

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [candidates[0][1]]


def try_detect_prose_paragraphs_tesseract(
    image: Image.Image,
    img_w: int,
    img_h: int,
    *,
    confidence_threshold: float,
) -> list[BubbleDetection] | None:
    from french_reader.paragraph_detector import (
        _cluster_lines_into_groups,
        _TextLine,
    )

    raw_lines = tesseract_lines_in_region(image, 0, 0, img_w, img_h, psm=3, min_conf=20)
    if not raw_lines or len(raw_lines) < 2:
        return None

    raw_lines = _filter_quality_tesseract_raw_lines(raw_lines, img_w, img_h, min_conf=0.35, illustrated=False)
    if len(raw_lines) < 2:
        return None

    lines = [_TextLine(x=x, y=y, w=w, h=h) for x, y, w, h, _conf in raw_lines]
    groups = _cluster_lines_into_groups(lines, img_w, img_h)

    results: list[BubbleDetection] = []
    for group in groups:
        if len(group) < 2:
            continue
        scored = _score_tesseract_group(group, img_w, img_h, illustrated=False)
        if scored is None:
            continue
        (x, y, bw, bh), confidence = scored
        if confidence < confidence_threshold:
            continue
        results.append(
            BubbleDetection(
                bbox=_normalize_bbox(x, y, bw, bh, img_w, img_h),
                confidence=confidence,
                detector="tesseract-paragraph",
            ),
        )

    return results or None


def try_detect_paragraphs_tesseract(
    image: Image.Image,
    *,
    confidence_threshold: float = 0.35,
) -> list[BubbleDetection] | None:
    if not tesseract_layout_available():
        return None

    try:
        import cv2
        import numpy as np
    except ImportError:
        return None

    arr = np.array(image)
    img_h, img_w = arr.shape[:2]
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    picture_book = try_detect_picture_book_paragraphs_tesseract(
        image,
        gray,
        img_w,
        img_h,
        confidence_threshold=confidence_threshold,
    )
    if picture_book is not None:
        return picture_book

    return try_detect_prose_paragraphs_tesseract(
        image,
        img_w,
        img_h,
        confidence_threshold=confidence_threshold,
    )
