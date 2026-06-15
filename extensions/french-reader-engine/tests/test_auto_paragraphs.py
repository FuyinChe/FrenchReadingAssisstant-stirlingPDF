from unittest.mock import patch

from fastapi.testclient import TestClient

from french_reader.main import app
from french_reader.paragraph_availability import ParagraphDetectorStatus

client = TestClient(app)


def test_paragraph_detector_status():
    response = client.get("/french-reader/ocr/paragraphs/status")
    assert response.status_code == 200
    body = response.json()
    assert "ready" in body
    assert "opencv_available" in body


@patch("french_reader.router.get_paragraph_detector_status")
@patch("french_reader.router.detect_text_paragraphs_from_base64")
def test_auto_paragraphs_endpoint(mock_detect, mock_status):
    from french_reader.bubble_detector import BubbleDetection
    from french_reader.schemas import BBox

    mock_status.return_value = ParagraphDetectorStatus(
        opencv_available=True,
        ready=True,
        detail="test",
    )
    mock_detect.return_value = [
        BubbleDetection(
            bbox=BBox(x=0.1, y=0.2, w=0.5, h=0.15),
            confidence=0.82,
            detector="opencv-paragraph",
        ),
        BubbleDetection(
            bbox=BBox(x=0.1, y=0.45, w=0.5, h=0.12),
            confidence=0.79,
            detector="opencv-paragraph",
        ),
    ]

    response = client.post(
        "/french-reader/ocr/auto-paragraphs",
        json={
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "page": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["detector"] == "opencv-paragraph"
    assert len(body["paragraphs"]) == 2
    assert body["paragraphs"][0]["order"] == 1
    assert body["paragraphs"][1]["order"] == 2


@patch("french_reader.router.get_paragraph_detector_status")
def test_auto_paragraphs_not_ready(mock_status):
    mock_status.return_value = ParagraphDetectorStatus(
        opencv_available=False,
        ready=False,
        detail="missing opencv",
    )

    response = client.post(
        "/french-reader/ocr/auto-paragraphs",
        json={
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "page": 1,
        },
    )

    assert response.status_code == 503
