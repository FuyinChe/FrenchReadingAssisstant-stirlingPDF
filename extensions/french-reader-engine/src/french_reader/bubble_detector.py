from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass

from PIL import Image

from french_reader.schemas import BBox

logger = logging.getLogger(__name__)

DEFAULT_YOLO_MODEL = "ogkalu/comic-speech-bubble-detector-yolov8m"

_yolo_model = None


@dataclass
class BubbleDetection:
    bbox: BBox
    confidence: float
    detector: str


def _decode_image(image_base64: str) -> Image.Image:
    raw = image_base64.strip()
    if "," in raw:
        raw = raw.split(",", 1)[1]
    data = base64.b64decode(raw)
    image = Image.open(io.BytesIO(data))
    return image.convert("RGB")


def _normalize_bbox(x: int, y: int, w: int, h: int, img_w: int, img_h: int) -> BBox:
    return BBox(
        x=max(0.0, min(1.0, x / img_w)),
        y=max(0.0, min(1.0, y / img_h)),
        w=max(0.001, min(1.0, w / img_w)),
        h=max(0.001, min(1.0, h / img_h)),
    )


def _bbox_iou(a: BBox, b: BBox) -> float:
    ax2 = a.x + a.w
    ay2 = a.y + a.h
    bx2 = b.x + b.w
    by2 = b.y + b.h
    ix1 = max(a.x, b.x)
    iy1 = max(a.y, b.y)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    inter_w = max(0.0, ix2 - ix1)
    inter_h = max(0.0, iy2 - iy1)
    inter = inter_w * inter_h
    if inter <= 0:
        return 0.0
    union = a.w * a.h + b.w * b.h - inter
    return inter / union if union > 0 else 0.0


def _contained_fraction(inner: tuple[int, int, int, int], outer: tuple[int, int, int, int]) -> float:
    ix, iy, iw, ih = inner
    ox, oy, ow, oh = outer
    inter_w = max(0, min(ix + iw, ox + ow) - max(ix, ox))
    inter_h = max(0, min(iy + ih, oy + oh) - max(iy, oy))
    inter = inter_w * inter_h
    inner_area = iw * ih
    return inter / inner_area if inner_area > 0 else 0.0


def _box_iou_xywh(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix1 = max(ax, bx)
    iy1 = max(ay, by)
    ix2 = min(ax + aw, bx + bw)
    iy2 = min(ay + ah, by + bh)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _expand_bbox(
    x: int,
    y: int,
    bw: int,
    bh: int,
    img_w: int,
    img_h: int,
    *,
    pad: float = 0.06,
) -> tuple[int, int, int, int]:
    px = int(bw * pad)
    py = int(bh * pad)
    x = max(0, x - px)
    y = max(0, y - py)
    x2 = min(img_w, x + bw + 2 * px)
    y2 = min(img_h, y + bh + 2 * py)
    return x, y, x2 - x, y2 - y


def _nms_bubbles(bubbles: list[BubbleDetection], iou_threshold: float = 0.45) -> list[BubbleDetection]:
    ordered = sorted(bubbles, key=lambda item: item.confidence, reverse=True)
    kept: list[BubbleDetection] = []
    for candidate in ordered:
        if any(_bbox_iou(candidate.bbox, kept_item.bbox) > iou_threshold for kept_item in kept):
            continue
        kept.append(candidate)
    return kept


def _boxes_overlap_significantly(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    inter_w = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    inter_h = max(0, min(ay + ah, by + bh) - max(ay, by))
    if inter_w <= 0 or inter_h <= 0:
        return False
    smaller_w = min(aw, bw)
    smaller_h = min(ah, bh)
    return inter_w / smaller_w >= 0.45 and inter_h / smaller_h >= 0.35


def _merge_candidate_boxes(
    boxes: list[tuple[int, int, int, int]],
    scores: list[float],
    *,
    iou_threshold: float = 0.38,
    contain_threshold: float = 0.75,
) -> list[tuple[tuple[int, int, int, int], float]]:
    if not boxes:
        return []

    order = sorted(
        range(len(boxes)),
        key=lambda index: scores[index] * boxes[index][2] * boxes[index][3],
        reverse=True,
    )
    kept: list[int] = []
    for index in order:
        candidate = boxes[index]
        candidate_merit = scores[index] * candidate[2] * candidate[3]
        replace: int | None = None
        blocked = False

        for kept_index in kept:
            kept_box = boxes[kept_index]
            if _contained_fraction(candidate, kept_box) >= contain_threshold:
                blocked = True
                break
            overlaps = (
                _box_iou_xywh(candidate, kept_box) > iou_threshold
                or _boxes_overlap_significantly(candidate, kept_box)
            )
            if not overlaps:
                continue
            kept_merit = scores[kept_index] * kept_box[2] * kept_box[3]
            if candidate_merit > kept_merit:
                replace = kept_index
            else:
                blocked = True
                break

        if blocked:
            continue
        if replace is not None:
            kept.remove(replace)
        kept.append(index)

    return [(boxes[index], scores[index]) for index in kept]


def _morph_kernel_size(img_w: int, img_h: int) -> int:
    ksize = max(7, min(img_w, img_h) // 90)
    return ksize + 1 if ksize % 2 == 0 else ksize


def preprocess_comic_page(image: Image.Image) -> Image.Image:
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("OpenCV is required for bubble preprocessing") from exc

    arr = np.array(image)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    rgb = cv2.cvtColor(filtered, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(rgb)


def _get_yolo_model(model_path: str):
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO

        _yolo_model = YOLO(model_path)
    return _yolo_model


def detect_bubbles_yolo(
    image: Image.Image,
    *,
    model_path: str,
    confidence_threshold: float,
) -> list[BubbleDetection] | None:
    try:
        import numpy as np
    except ImportError:
        return None

    try:
        model = _get_yolo_model(model_path)
        results = model.predict(
            source=np.array(image),
            conf=confidence_threshold,
            verbose=False,
        )
    except Exception as exc:
        logger.warning("YOLO bubble detection failed: %s", exc)
        return None

    img_w, img_h = image.size
    detections: list[BubbleDetection] = []
    for result in results or []:
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            continue
        for box in boxes:
            xyxy = box.xyxy[0].tolist()
            x1, y1, x2, y2 = (int(v) for v in xyxy)
            conf = float(box.conf[0])
            bw = max(1, x2 - x1)
            bh = max(1, y2 - y1)
            detections.append(
                BubbleDetection(
                    bbox=_normalize_bbox(x1, y1, bw, bh, img_w, img_h),
                    confidence=conf,
                    detector="yolo",
                ),
            )

    return _nms_bubbles(detections)


def _score_bubble_contour(
    contour,
    gray,
    sat,
    img_w: int,
    img_h: int,
    *,
    confidence_threshold: float,
) -> tuple[int, int, int, int, float] | None:
    import cv2
    import numpy as np

    edge_area = cv2.contourArea(contour)
    x, y, bw, bh = cv2.boundingRect(contour)
    bbox_area = bw * bh
    page_area = img_w * img_h
    min_area = page_area * 0.0018
    max_area = page_area * 0.12

    if bbox_area < 8000:
        return None
    if edge_area < min_area * 0.5 and edge_area < 2000:
        return None
    if bw < 30 or bh < 24:
        return None

    roi_sat = sat[y : y + bh, x : x + bw]
    colorful = float(np.sum(roi_sat > 50) / roi_sat.size)

    height_ratio = bh / img_h
    if height_ratio > 0.30:
        return None
    if height_ratio > 0.20 and colorful > 0.35:
        return None
    if bw > img_w * 0.55:
        return None

    aspect = bw / bh if bh else 0.0
    if aspect < 0.2 or aspect > 7.0:
        return None
    if bh < 55 and aspect > 3.2:
        return None
    if bh < 42 and aspect > 2.0:
        return None
    if bbox_area > max_area:
        return None
    if bbox_area / page_area > 0.105 and bw > img_w * 0.48:
        return None

    if colorful > 0.47:
        return None

    bbox_gray = gray[y : y + bh, x : x + bw]
    mean_brightness = float(bbox_gray.mean())
    white_ratio = float(np.sum(bbox_gray > 175) / bbox_gray.size)
    light_ratio = float(np.sum(bbox_gray > 140) / bbox_gray.size)

    if mean_brightness < 190 and white_ratio < 0.92:
        return None

    interior_ok = (
        (mean_brightness >= 195 and white_ratio >= 0.60)
        or (mean_brightness >= 165 and light_ratio >= 0.72)
        or (mean_brightness >= 150 and light_ratio >= 0.65 and white_ratio >= 0.35)
    )
    if not interior_ok:
        return None

    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    filled_area = cv2.countNonZero(mask)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = edge_area / hull_area if hull_area > 0 else 0.0
    extent = edge_area / bbox_area if bbox_area else 0.0
    fill_extent = filled_area / bbox_area if bbox_area else 0.0

    bright_bubble = mean_brightness >= 210 and white_ratio >= 0.78 and colorful <= 0.15
    if bright_bubble:
        if fill_extent < 0.15 and extent < 0.22:
            return None
        if solidity < 0.30:
            return None
    elif solidity < 0.72 or extent < 0.38:
        return None

    confidence = min(
        0.95,
        light_ratio * 0.4 + (mean_brightness / 255.0) * 0.35 + max(solidity, fill_extent) * 0.25,
    )
    if confidence < confidence_threshold:
        return None

    ex, ey, ew, eh = _expand_bbox(x, y, bw, bh, img_w, img_h)
    expanded_height_ratio = eh / img_h
    if (
        expanded_height_ratio > 0.26
        and ((ey + eh) / img_h) > 0.52
        and colorful < 0.25
    ):
        return None

    return ex, ey, ew, eh, confidence


def _collect_outline_candidates(gray, sat, img_w: int, img_h: int, *, confidence_threshold: float):
    import cv2

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    boxes: list[tuple[int, int, int, int]] = []
    scores: list[float] = []

    def add_contours(contours) -> None:
        for contour in contours:
            scored = _score_bubble_contour(
                contour,
                gray,
                sat,
                img_w,
                img_h,
                confidence_threshold=confidence_threshold,
            )
            if scored is not None:
                x, y, bw, bh, confidence = scored
                boxes.append((x, y, bw, bh))
                scores.append(confidence)

    for ksize in (9, 11, 13, 15, 17):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
        ink_mask = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            8,
        )
        closed = cv2.morphologyEx(ink_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        add_contours(cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])

    for low, high in ((25, 90), (20, 80)):
        edges = cv2.Canny(blurred, low, high)
        for ksize in (5, 7, 9, 11, 15, 19, 23):
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
            closed = cv2.dilate(
                closed,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
                iterations=1,
            )
            add_contours(cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0])

    return boxes, scores


def _collect_color_outline_candidates(gray, sat, hsv, img_w, img_h, *, confidence_threshold: float):
    import cv2

    boxes: list[tuple[int, int, int, int]] = []
    scores: list[float] = []

    purple = cv2.inRange(hsv, (125, 20, 60), (170, 255, 255))
    orange = cv2.inRange(hsv, (5, 50, 90), (35, 255, 255))
    dark = cv2.inRange(gray, 0, 90)
    color_edges = cv2.bitwise_or(purple, cv2.bitwise_or(orange, dark))

    for ksize in (9, 13, 17):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
        closed = cv2.morphologyEx(color_edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        for contour in contours:
            scored = _score_bubble_contour(
                contour,
                gray,
                sat,
                img_w,
                img_h,
                confidence_threshold=confidence_threshold,
            )
            if scored is not None:
                x, y, bw, bh, confidence = scored
                boxes.append((x, y, bw, bh))
                scores.append(confidence)

    return boxes, scores


def _collect_gradient_candidates(gray, sat, img_w, img_h, *, confidence_threshold: float):
    import cv2

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    gradient = cv2.morphologyEx(
        blurred,
        cv2.MORPH_GRADIENT,
        cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
    )
    _, grad_bin = cv2.threshold(gradient, 25, 255, cv2.THRESH_BINARY)

    boxes: list[tuple[int, int, int, int]] = []
    scores: list[float] = []
    for ksize in (11, 15, 19):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
        closed = cv2.morphologyEx(grad_bin, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        for contour in contours:
            scored = _score_bubble_contour(
                contour,
                gray,
                sat,
                img_w,
                img_h,
                confidence_threshold=confidence_threshold,
            )
            if scored is not None:
                x, y, bw, bh, confidence = scored
                boxes.append((x, y, bw, bh))
                scores.append(confidence)

    return boxes, scores


def _detect_bubbles_from_bright_regions(
    gray,
    sat,
    img_w: int,
    img_h: int,
    *,
    confidence_threshold: float,
) -> list[tuple[tuple[int, int, int, int], float]]:
    import cv2

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, bright = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    closed = cv2.morphologyEx(bright, cv2.MORPH_CLOSE, kernel)

    boxes: list[tuple[int, int, int, int]] = []
    scores: list[float] = []
    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for contour in contours:
        scored = _score_bubble_contour(
            contour,
            gray,
            sat,
            img_w,
            img_h,
            confidence_threshold=confidence_threshold,
        )
        if scored is not None:
            x, y, bw, bh, confidence = scored
            boxes.append((x, y, bw, bh))
            scores.append(confidence)

    return _merge_candidate_boxes(boxes, scores)


def detect_bubbles_opencv(
    image: Image.Image,
    *,
    confidence_threshold: float,
) -> list[BubbleDetection]:
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Bubble detection requires OpenCV. Install with:\n"
            "  cd extensions/french-reader-engine && uv sync --extra bubble",
        ) from exc

    arr = np.array(image)
    img_h, img_w = arr.shape[:2]
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    sat = hsv[:, :, 1]

    boxes: list[tuple[int, int, int, int]] = []
    scores: list[float] = []

    for candidate_boxes, candidate_scores in (
        _collect_outline_candidates(
            gray,
            sat,
            img_w,
            img_h,
            confidence_threshold=confidence_threshold,
        ),
        _collect_color_outline_candidates(
            gray,
            sat,
            hsv,
            img_w,
            img_h,
            confidence_threshold=confidence_threshold,
        ),
        _collect_gradient_candidates(
            gray,
            sat,
            img_w,
            img_h,
            confidence_threshold=confidence_threshold,
        ),
    ):
        boxes.extend(candidate_boxes)
        scores.extend(candidate_scores)

    merged = _merge_candidate_boxes(boxes, scores)
    if merged:
        return [
            BubbleDetection(
                bbox=_normalize_bbox(x, y, bw, bh, img_w, img_h),
                confidence=confidence,
                detector="opencv",
            )
            for (x, y, bw, bh), confidence in merged
        ]

    fallback = _detect_bubbles_from_bright_regions(
        gray,
        sat,
        img_w,
        img_h,
        confidence_threshold=confidence_threshold,
    )
    return [
        BubbleDetection(
            bbox=_normalize_bbox(x, y, bw, bh, img_w, img_h),
            confidence=confidence,
            detector="opencv",
        )
        for (x, y, bw, bh), confidence in fallback
    ]


def detect_speech_bubbles(
    image_base64: str,
    *,
    confidence_threshold: float = 0.35,
    preprocess: bool = False,
    prefer_yolo: bool = True,
    yolo_model_path: str = DEFAULT_YOLO_MODEL,
) -> tuple[list[BubbleDetection], str]:
    image = _decode_image(image_base64)
    if preprocess:
        image = preprocess_comic_page(image)

    if prefer_yolo:
        yolo_results = detect_bubbles_yolo(
            image,
            model_path=yolo_model_path,
            confidence_threshold=confidence_threshold,
        )
        if yolo_results:
            return yolo_results, "yolo"

    opencv_results = detect_bubbles_opencv(
        image,
        confidence_threshold=confidence_threshold,
    )
    return opencv_results, "opencv"
