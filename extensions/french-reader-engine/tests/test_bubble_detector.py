import base64
import io
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from french_reader.bubble_detector import (
    detect_bubbles_opencv,
    detect_speech_bubbles,
    preprocess_comic_page,
)

pytest.importorskip("cv2")

COOKBOOK_FIXTURE = (
    Path.home()
    / ".cursor"
    / "projects"
    / "Users-fuyinche-Documents-GitHub-FrenchPdfReader"
    / "assets"
    / "Screenshot_2026-06-13_at_11.51.27_PM-0fd7ba35-604f-4cbb-8c4d-b74184c0c074.png"
)
COOKBOOK_FIXTURE_2 = (
    Path.home()
    / ".cursor"
    / "projects"
    / "Users-fuyinche-Documents-GitHub-FrenchPdfReader"
    / "assets"
    / "Screenshot_2026-06-13_at_11.59.15_PM-5e5a8b58-b2a8-4e1c-8ecf-359b6eef7ca8.png"
)


def _bubble_page_base64() -> str:
    image = Image.new("RGB", (400, 300), color=(120, 120, 120))
    draw = ImageDraw.Draw(image)
    draw.ellipse((40, 40, 180, 120), fill="white", outline="black", width=3)
    draw.ellipse((220, 150, 360, 250), fill="white", outline="black", width=3)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _white_page_bubbles_base64() -> str:
    """White bubbles with black outlines on a white page (BD / cookbook style)."""
    image = Image.new("RGB", (800, 600), color="white")
    draw = ImageDraw.Draw(image)
    bubbles = [
        (30, 40, 320, 170),
        (450, 50, 760, 170),
        (280, 220, 560, 320),
        (600, 280, 770, 380),
    ]
    for x1, y1, x2, y2 in bubbles:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill="white", outline="black", width=3)
        draw.text((x1 + 20, y1 + 30), "Bonjour!", fill="black")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def test_preprocess_comic_page_returns_rgb_image():
    image = Image.new("RGB", (120, 80), color=(90, 90, 90))
    processed = preprocess_comic_page(image)
    assert processed.mode == "RGB"
    assert processed.size == image.size


def test_detect_bubbles_opencv_finds_white_regions_on_gray_background():
    image = Image.open(io.BytesIO(base64.b64decode(_bubble_page_base64())))
    detections = detect_bubbles_opencv(image, confidence_threshold=0.3)
    assert len(detections) >= 1
    assert all(item.detector == "opencv" for item in detections)
    assert all(0 <= item.bbox.x <= 1 for item in detections)


def test_detect_bubbles_opencv_finds_outlined_bubbles_on_white_page():
    image = Image.open(io.BytesIO(base64.b64decode(_white_page_bubbles_base64())))
    detections = detect_bubbles_opencv(image, confidence_threshold=0.3)
    assert len(detections) >= 3


def test_detect_speech_bubbles_uses_opencv_when_yolo_unavailable():
    detections, detector = detect_speech_bubbles(
        _bubble_page_base64(),
        confidence_threshold=0.3,
        prefer_yolo=False,
    )
    assert detector == "opencv"
    assert len(detections) >= 1


@pytest.mark.skipif(not COOKBOOK_FIXTURE.exists(), reason="local screenshot fixture not available")
def test_detect_bubbles_on_cookbook_fixture():
    image = Image.open(COOKBOOK_FIXTURE).convert("RGB")
    detections = detect_bubbles_opencv(image, confidence_threshold=0.3)
    assert len(detections) == 4


@pytest.mark.skipif(not COOKBOOK_FIXTURE_2.exists(), reason="local screenshot fixture not available")
def test_detect_bubbles_on_multi_bubble_cookbook_fixture():
    image = Image.open(COOKBOOK_FIXTURE_2).convert("RGB")
    detections = detect_bubbles_opencv(image, confidence_threshold=0.3)
    assert len(detections) == 8
