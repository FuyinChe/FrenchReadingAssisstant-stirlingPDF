import base64
import io
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from french_reader.bubble_availability import BubbleDetectorStatus
from french_reader.bubble_detector import BubbleDetection
from french_reader.main import app
from french_reader.schemas import BBox

client = TestClient(app)


def _sample_png_base64() -> str:
    image = Image.new("RGB", (300, 200), color=(100, 100, 100))
    draw = ImageDraw.Draw(image)
    draw.ellipse((30, 30, 140, 100), fill="white", outline="black", width=2)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def test_bubble_status_endpoint():
    response = client.get("/french-reader/ocr/bubbles/status")
    assert response.status_code == 200
    body = response.json()
    assert "ready" in body
    assert "opencv_available" in body


@patch("french_reader.router.get_bubble_detector_status")
@patch("french_reader.router.detect_speech_bubbles")
def test_auto_bubbles_success(mock_detect, mock_status):
    mock_status.return_value = BubbleDetectorStatus(
        opencv_available=True,
        yolo_available=False,
        ready=True,
        detail="test",
    )
    mock_detect.return_value = (
        [
            BubbleDetection(
                bbox=BBox(x=0.1, y=0.1, w=0.3, h=0.2),
                confidence=0.88,
                detector="opencv",
            ),
        ],
        "opencv",
    )

    response = client.post(
        "/french-reader/ocr/auto-bubbles",
        json={
            "image_base64": _sample_png_base64(),
            "page": 2,
            "confidence_threshold": 0.3,
            "preprocess": True,
            "prefer_yolo": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["detector"] == "opencv"
    assert body["preprocess"] is True
    assert len(body["bubbles"]) == 1
    assert body["bubbles"][0]["confidence"] == 0.88


@patch("french_reader.router.get_bubble_detector_status")
def test_auto_bubbles_not_ready(mock_status):
    mock_status.return_value = BubbleDetectorStatus(
        opencv_available=False,
        yolo_available=False,
        ready=False,
        detail="missing",
    )

    response = client.post(
        "/french-reader/ocr/auto-bubbles",
        json={
            "image_base64": _sample_png_base64(),
            "page": 1,
        },
    )
    assert response.status_code == 503
