from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from french_reader.paragraph_detector import detect_text_paragraphs
from tests.regression_assets import regression_assets_dir

pytest.importorskip("cv2")


def _draw_wrapped_paragraph(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    lines: list[str],
    *,
    line_height: int,
    font,
) -> int:
    cursor_y = y
    for line in lines:
        draw.text((x, cursor_y), line, fill="black", font=font)
        cursor_y += line_height
    return cursor_y


def _synthetic_prose_page() -> Image.Image:
    image = Image.new("RGB", (720, 960), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    y = 70
    y = _draw_wrapped_paragraph(
        draw,
        72,
        y,
        [
            "Ceci est le premier paragraphe du document.",
            "Il contient plusieurs lignes de texte francais.",
            "Chaque ligne doit etre regroupee ensemble.",
            "Nous voulons une seule zone OCR par paragraphe.",
        ],
        line_height=30,
        font=font,
    )
    y += 36
    y = _draw_wrapped_paragraph(
        draw,
        72,
        y,
        [
            "Voici le deuxieme paragraphe, separe par un espace.",
            "Il possede aussi plusieurs lignes successives.",
            "Le detecteur doit produire deux regions distinctes.",
        ],
        line_height=30,
        font=font,
    )
    y += 36
    _draw_wrapped_paragraph(
        draw,
        72,
        y,
        [
            "Enfin, un troisieme paragraphe plus court.",
            "Il sert a verifier la stabilite du regroupement.",
        ],
        line_height=30,
        font=font,
    )
    return image


def _two_column_prose_page() -> Image.Image:
    image = Image.new("RGB", (900, 700), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    left_lines = [
        "Colonne gauche ligne un du texte.",
        "Colonne gauche ligne deux du texte.",
        "Colonne gauche ligne trois du texte.",
    ]
    right_lines = [
        "Colonne droite ligne un du texte.",
        "Colonne droite ligne deux du texte.",
        "Colonne droite ligne trois du texte.",
    ]

    y = 80
    for left, right in zip(left_lines, right_lines):
        draw.text((60, y), left, fill="black", font=font)
        draw.text((470, y), right, fill="black", font=font)
        y += 30

    y += 34
    for line in [
        "Paragraphe bas sur toute la largeur, premiere ligne.",
        "Paragraphe bas sur toute la largeur, deuxieme ligne.",
    ]:
        draw.text((60, y), line, fill="black", font=font)
        y += 30

    return image


def test_detects_multiple_paragraph_blocks_on_synthetic_page():
    detections = detect_text_paragraphs(_synthetic_prose_page(), confidence_threshold=0.3)
    assert len(detections) == 3
    assert all(item.detector in {"opencv-paragraph", "tesseract-paragraph"} for item in detections)


def test_paragraph_boxes_are_multi_line_not_single_words():
    detections = detect_text_paragraphs(_synthetic_prose_page(), confidence_threshold=0.3)
    heights = sorted(item.bbox.h for item in detections)
    assert heights[0] > 0.035
    assert max(heights) < 0.35


def test_two_column_page_keeps_columns_separate():
    detections = detect_text_paragraphs(_two_column_prose_page(), confidence_threshold=0.3)
    assert len(detections) >= 3

    left = [
        item for item in detections if (item.bbox.x + item.bbox.w / 2) < 0.42
    ]
    right = [
        item
        for item in detections
        if (item.bbox.x + item.bbox.w / 2) >= 0.42 and item.bbox.w < 0.3
    ]
    full_width = [item for item in detections if item.bbox.w > 0.24]

    assert len(left) >= 1
    assert len(right) >= 1
    assert len(full_width) >= 1


def _pdf_like_prose_page() -> Image.Image:
    image = Image.new("RGB", (1240, 1754), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    margin_x = 120
    line_height = 34
    y = 160

    blocks = [
        [
            "Il etait une fois une petite fille de village, la plus jolie qu'on eut su voir:",
            "sa mere en etait folle, sa grand-mere encore plus. Cette bonne femme lui fit faire",
            "un petit chaperon rouge, qui lui seyait si bien, que l'on l'appela partout le Petit",
            "Chaperon rouge.",
        ],
        [
            "Un jour, sa mere, ayant cuit et fait des galettes, lui dit: Va voir comment se porte",
            "ta grand-mere, car on m'a avisée qu'elle etait malade. Porte-lui une galette et ce",
            "petit pot de beurre.",
        ],
        [
            "Le Petit Chaperon rouge partit aussitot pour aller chez sa grand-mere, qui demeurait",
            "dans un autre village.",
        ],
    ]

    for block in blocks:
        for line in block:
            draw.text((margin_x, y), line, fill="black", font=font)
            y += line_height
        y += line_height

    return image


def test_pdf_like_page_detects_multiple_paragraphs():
    detections = detect_text_paragraphs(_pdf_like_prose_page(), confidence_threshold=0.3)
    assert len(detections) >= 2
    assert all(item.detector in {"opencv-paragraph", "tesseract-paragraph"} for item in detections)


def _picture_book_text_with_illustration_page() -> Image.Image:
    image = Image.new("RGB", (800, 1000), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    y = 40
    for line in [
        "Ca ne se passe pas toujours ainsi.",
        "La mamie de Leon, un copain d'Alice, a prefere",
        "que son corps soit incinere plutot qu'enterre.",
        "Le corps est brule, et les cendres sont conservees",
        "dans une sorte de boite, une urne.",
    ]:
        draw.text((60, y), line, fill=(30, 30, 30), font=font)
        y += 28

    draw.rectangle((300, 600, 500, 640), fill=(25, 45, 110))
    draw.ellipse((320, 620, 480, 820), fill=(25, 45, 110))
    return image


def test_picture_book_page_prefers_text_over_illustration():
    detections = detect_text_paragraphs(
        _picture_book_text_with_illustration_page(),
        confidence_threshold=0.3,
    )
    assert len(detections) == 1
    box = detections[0].bbox
    assert box.y + box.h < 0.55


def test_picture_book_right_boundary_covers_line_endings():
    detections = detect_text_paragraphs(
        _picture_book_text_with_illustration_page(),
        confidence_threshold=0.3,
    )
    box = detections[0].bbox
    assert box.x + box.w >= 0.38
    assert box.h >= 0.12


def test_picture_book_wide_lines_extend_to_right_margin():
    image = Image.new("RGB", (800, 520), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    y = 36
    for line in [
        "La mamie de Leon, un copain d'Alice, a prefere que son corps",
        "soit incinere plutot qu'enterre. Le corps est brule, et les",
        "cendres sont conservees dans une sorte de boite, une urne.",
    ]:
        draw.text((56, y), line, fill=(25, 25, 25), font=font)
        y += 30

    detections = detect_text_paragraphs(image, confidence_threshold=0.3)
    assert len(detections) == 1
    box = detections[0].bbox
    assert box.x + box.w >= 0.44


def test_paragraph_preprocess_keeps_text_block():
    from french_reader.bubble_detector import preprocess_paragraph_page

    image = preprocess_paragraph_page(_picture_book_text_with_illustration_page())
    detections = detect_text_paragraphs(image, confidence_threshold=0.3)
    assert len(detections) == 1
    box = detections[0].bbox
    assert box.y + box.h < 0.55
    assert box.x + box.w >= 0.38


def _picture_book_fixture_paths():
    assets = regression_assets_dir()
    if assets is None:
        return []
    return sorted(assets.glob("Screenshot_2026-06-14*.png"))


@pytest.mark.parametrize("fixture_path", _picture_book_fixture_paths())
def test_picture_book_fixtures_detect_single_paragraph_block(fixture_path: Path):
    detections = detect_text_paragraphs(
        Image.open(fixture_path).convert("RGB"),
        confidence_threshold=0.3,
    )
    assert len(detections) == 1
    assert detections[0].bbox.h > 0.04
    assert detections[0].bbox.w > 0.2
