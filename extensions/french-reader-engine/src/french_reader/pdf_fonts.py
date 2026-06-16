"""Register PDF fonts for French, IPA, and CJK export."""

from __future__ import annotations

import io
import sys
from functools import lru_cache
from pathlib import Path

from importlib.resources import files

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

FONT_LATIN = "CharisSIL"
FONT_LATIN_BOLD = "CharisSIL-Bold"
FONT_LATIN_ITALIC = "CharisSIL-Italic"
FONT_CJK = "STSong-Light"


def _font_file_path(filename: str) -> Path:
    try:
        path = files("french_reader").joinpath("assets/fonts", filename)
        if path.is_file():
            return Path(str(path))
    except (FileNotFoundError, OSError, TypeError, ValueError):
        pass

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            frozen = Path(meipass) / "french_reader" / "assets" / "fonts" / filename
            if frozen.is_file():
                return frozen

    package = Path(__file__).resolve().parent / "assets" / "fonts" / filename
    if package.is_file():
        return package

    raise FileNotFoundError(f"Export font not found: {filename}")


def _load_font_bytes(filename: str) -> bytes:
    return _font_file_path(filename).read_bytes()


@lru_cache(maxsize=1)
def register_export_fonts() -> None:
    if FONT_LATIN in pdfmetrics.getRegisteredFontNames():
        return

    pdfmetrics.registerFont(TTFont(FONT_LATIN, io.BytesIO(_load_font_bytes("CharisSIL-Regular.ttf"))))
    pdfmetrics.registerFont(TTFont(FONT_LATIN_BOLD, io.BytesIO(_load_font_bytes("CharisSIL-Bold.ttf"))))
    pdfmetrics.registerFont(
        TTFont(FONT_LATIN_ITALIC, io.BytesIO(_load_font_bytes("CharisSIL-Italic.ttf")))
    )
    pdfmetrics.registerFontFamily(
        FONT_LATIN,
        normal=FONT_LATIN,
        bold=FONT_LATIN_BOLD,
        italic=FONT_LATIN_ITALIC,
        boldItalic=FONT_LATIN_BOLD,
    )
    pdfmetrics.registerFont(UnicodeCIDFont(FONT_CJK))
