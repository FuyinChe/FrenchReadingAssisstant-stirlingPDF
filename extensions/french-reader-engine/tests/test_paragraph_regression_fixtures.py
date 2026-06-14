from pathlib import Path

import pytest
from PIL import Image

from french_reader.paragraph_detector import detect_text_paragraphs
from tests.regression_assets import regression_assets_dir

pytest.importorskip("cv2")


def _fixture(name: str) -> Path | None:
    assets = regression_assets_dir()
    if assets is None:
        return None
    return assets / name


REGRESSION_PAGES = [
    pytest.param(
        "Screenshot_2026-06-14_at_7.31.42_PM-1a5f4588-64ac-4e16-ac66-c359b60f4448.png",
        {"placement": "top", "min_right": 0.72, "max_h": 0.28},
        id="urn-top-text",
    ),
    pytest.param(
        "Screenshot_2026-06-14_at_7.32.20_PM-3d72aa4f-4541-4091-9b72-1f0366d55e10.png",
        {"placement": "top", "min_right": 0.75, "max_h": 0.22},
        id="alice-worried-top",
    ),
    pytest.param(
        "Screenshot_2026-06-14_at_7.32.54_PM-f861b4aa-cc4a-4dab-bc54-e6e3f16acbcc.png",
        {"placement": "top", "min_right": 0.70, "max_h": 0.22},
        id="dark-background-top",
    ),
    pytest.param(
        "Screenshot_2026-06-14_at_7.33.58_PM-f53ccd88-4e9d-4313-811c-19b79efbc5b5.png",
        {"placement": "top", "min_right": 0.72, "max_h": 0.20},
        id="bedtime-top",
    ),
    pytest.param(
        "Screenshot_2026-06-14_at_7.34.28_PM-50b7b663-3d57-4af0-9b7b-0b4a7e808986.png",
        {"placement": "bottom", "min_y": 0.50, "min_cy": 0.58, "max_h": 0.25},
        id="memories-bottom-text",
    ),
    pytest.param(
        "Screenshot_2026-06-14_at_7.35.18_PM-7e9e93e8-9a86-4b7a-befd-28b96e8e3f19.png",
        {"placement": "top", "min_right": 0.72, "max_h": 0.20},
        id="parents-couch-top",
    ),
    pytest.param(
        "Screenshot_2026-06-14_at_7.36.36_PM-3c8889a1-650c-4328-97bf-c28847d55969.png",
        {"placement": "top", "min_right": 0.80, "max_h": 0.20},
        id="petite-taupe-top",
    ),
]


@pytest.mark.parametrize("filename, expectations", REGRESSION_PAGES)
def test_picture_book_regression_fixtures(filename: str, expectations: dict):
    path = _fixture(filename)
    if path is None or not path.is_file():
        pytest.skip(f"fixture missing: {filename}")

    detections = detect_text_paragraphs(
        Image.open(path).convert("RGB"),
        confidence_threshold=0.3,
    )
    assert len(detections) == 1, f"expected one paragraph, got {len(detections)}"

    box = detections[0].bbox
    cy = box.y + box.h / 2
    right = box.x + box.w

    assert right >= expectations.get("min_right", 0.65)
    assert box.h <= expectations.get("max_h", 0.35)

    if expectations["placement"] == "top":
        assert cy <= 0.32, f"paragraph center too low ({cy:.3f}) — likely illustration"
        assert box.y <= 0.20
    else:
        assert cy >= expectations.get("min_cy", 0.55)
        assert box.y >= expectations.get("min_y", 0.48)

    # Illustration belt in the middle of the page should not dominate the box.
    illustration_overlap = max(0.0, min(box.y + box.h, 0.58) - max(box.y, 0.32))
    assert illustration_overlap / box.h <= 0.35
