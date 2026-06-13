import base64
import io
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont

from french_reader.main import app
from french_reader.ocr_service import OcrRecognition

client = TestClient(app)


def _sample_png_base64(text: str = "Bonjour") -> str:
    image = Image.new("RGB", (200, 60), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 15), text, fill="black")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def test_ocr_region_success():
    mock = OcrRecognition(
        text="Bonjour le monde",
        confidence=0.92,
        lines=[("Bonjour le monde", 0.92)],
    )
    with patch("french_reader.router.recognize_french", return_value=mock):
        response = client.post(
            "/french-reader/ocr/region",
            json={
                "image_base64": _sample_png_base64(),
                "page": 1,
                "bbox": {"x": 0.1, "y": 0.1, "w": 0.5, "h": 0.2},
                "lang": "fr",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Bonjour le monde"
    assert body["confidence"] == 0.92
    assert len(body["lines"]) == 1


def test_ocr_region_invalid_bbox():
    response = client.post(
        "/french-reader/ocr/region",
        json={
            "image_base64": _sample_png_base64(),
            "page": 1,
            "bbox": {"x": 0, "y": 0, "w": 0, "h": 0.2},
        },
    )
    assert response.status_code == 422
