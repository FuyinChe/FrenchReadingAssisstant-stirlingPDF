from __future__ import annotations

import re
from xml.sax.saxutils import escape

from french_reader.pdf_fonts import FONT_CJK, FONT_LATIN, FONT_LATIN_BOLD, FONT_LATIN_ITALIC

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_CODE_RE = re.compile(r"`([^`]+)`")
_BULLET_RE = re.compile(r"^[\-\*•]\s+")
_CJK_RE = re.compile(
    r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3000-\u303f\uff00-\uffef]+"
)


def markdown_to_reportlab_html(text: str) -> str:
    """Convert a small Markdown subset to ReportLab Paragraph markup."""
    lines = text.split("\n")
    if not lines:
        return "&nbsp;"

    html_lines: list[str] = []
    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            html_lines.append("&nbsp;")
            continue

        bullet = bool(_BULLET_RE.match(line))
        if bullet:
            line = _BULLET_RE.sub("", line, count=1)

        converted = _convert_inline_markdown(line)
        if bullet:
            converted = f"• {converted}"
        html_lines.append(converted or "&nbsp;")

    html = "<br/>".join(html_lines)
    return wrap_cjk_segments(html)


def wrap_cjk_segments(html: str) -> str:
    return _CJK_RE.sub(lambda match: f'<font name="{FONT_CJK}">{match.group(0)}</font>', html)


def _convert_inline_markdown(line: str) -> str:
    escaped = escape(line)
    escaped = _BOLD_RE.sub(rf'<font name="{FONT_LATIN_BOLD}">\1</font>', escaped)
    escaped = _ITALIC_RE.sub(rf'<font name="{FONT_LATIN_ITALIC}">\1</font>', escaped)
    escaped = _CODE_RE.sub(rf'<font name="{FONT_LATIN}">\1</font>', escaped)
    return escaped
