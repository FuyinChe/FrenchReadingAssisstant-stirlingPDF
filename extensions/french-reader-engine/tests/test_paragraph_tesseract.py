from unittest.mock import patch

from PIL import Image, ImageDraw, ImageFont

from french_reader.paragraph_detector import detect_text_paragraphs
from french_reader.paragraph_tesseract import try_detect_paragraphs_tesseract

pytest = __import__("pytest")
pytest.importorskip("cv2")


def _sample_page() -> Image.Image:
    image = Image.new("RGB", (800, 520), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    y = 36
    for line in [
        "Ca ne se passe pas toujours ainsi.",
        "La mamie de Leon, un copain d'Alice, a prefere que son corps",
        "soit incinere plutot qu'enterre.",
    ]:
        draw.text((56, y), line, fill=(25, 25, 25), font=font)
        y += 30
    return image


def _fake_tesseract_lines(*_args, **_kwargs):
    return [
        (56, 36, 280, 12, 0.91),
        (56, 66, 310, 12, 0.89),
        (56, 96, 295, 12, 0.9),
    ]


@patch("french_reader.paragraph_tesseract.tesseract_layout_available", return_value=True)
@patch(
    "french_reader.paragraph_tesseract.tesseract_lines_in_region",
    side_effect=lambda *_a, **_k: _fake_tesseract_lines(),
)
def test_detect_paragraphs_prefers_tesseract_when_available(_lines, _available):
    detections = detect_text_paragraphs(_sample_page(), confidence_threshold=0.3)
    assert len(detections) == 1
    assert detections[0].detector == "tesseract-paragraph"
    assert detections[0].bbox.x + detections[0].bbox.w >= 0.42


@patch("french_reader.paragraph_tesseract.try_detect_paragraphs_tesseract", return_value=None)
def test_detect_paragraphs_falls_back_to_opencv(_tesseract):
    from test_paragraph_detector import _picture_book_text_with_illustration_page

    detections = detect_text_paragraphs(
        _picture_book_text_with_illustration_page(),
        confidence_threshold=0.3,
    )
    assert len(detections) >= 1
    assert detections[0].detector == "opencv-paragraph"


@patch("french_reader.paragraph_tesseract.tesseract_layout_available", return_value=True)
@patch("french_reader.paragraph_tesseract.tesseract_lines_in_region", return_value=None)
def test_try_detect_paragraphs_tesseract_returns_none_without_lines(_lines, _available):
    assert try_detect_paragraphs_tesseract(_sample_page()) is None
