from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OcrEngineStatus:
    name: str
    available: bool
    detail: str


def _tesseract_langs() -> set[str]:
    import subprocess

    if not shutil.which("tesseract"):
        return set()
    try:
        out = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return set()
    langs: set[str] = set()
    for line in out.stdout.splitlines():
        line = line.strip()
        if line and not line.startswith("List of"):
            langs.add(line)
    return langs


def _paddle_available() -> tuple[bool, str]:
    try:
        import paddleocr  # noqa: F401
        import paddle  # noqa: F401
    except ImportError as exc:
        return False, f"not installed ({exc})"
    except Exception as exc:
        return False, str(exc)
    return True, "import ok"


def get_ocr_engine_status() -> list[OcrEngineStatus]:
    statuses: list[OcrEngineStatus] = []

    tesseract_bin = shutil.which("tesseract")
    langs = _tesseract_langs()
    if tesseract_bin:
        fra = "fra" in langs
        statuses.append(
            OcrEngineStatus(
                name="tesseract",
                available=fra or bool(langs),
                detail=f"binary={tesseract_bin}, langs={sorted(langs) or ['none']}",
            ),
        )
    else:
        statuses.append(
            OcrEngineStatus(
                name="tesseract",
                available=False,
                detail="binary not found — run ./scripts/setup-ocr.sh",
            ),
        )

    try:
        import pytesseract  # noqa: F401

        py_ok = True
        py_detail = "installed"
    except ImportError:
        py_ok = False
        py_detail = "pytesseract not installed — uv sync --extra ocr"

    statuses.append(
        OcrEngineStatus(name="pytesseract", available=py_ok, detail=py_detail),
    )

    paddle_ok, paddle_detail = _paddle_available()
    statuses.append(
        OcrEngineStatus(name="paddleocr", available=paddle_ok, detail=paddle_detail),
    )

    return statuses


def any_ocr_engine_ready() -> bool:
    statuses = get_ocr_engine_status()
    tesseract = next((s for s in statuses if s.name == "tesseract"), None)
    pytesseract_s = next((s for s in statuses if s.name == "pytesseract"), None)
    if tesseract and pytesseract_s and tesseract.available and pytesseract_s.available:
        return True
    paddle = next((s for s in statuses if s.name == "paddleocr"), None)
    return bool(paddle and paddle.available)


def format_setup_hint() -> str:
    return (
        "OCR is not configured. From the repo root run:\n"
        "  ./scripts/setup-ocr.sh\n"
        "  cd extensions/french-reader-engine && uv sync --dev --extra ocr\n"
        "Then restart ./scripts/dev.sh"
    )
