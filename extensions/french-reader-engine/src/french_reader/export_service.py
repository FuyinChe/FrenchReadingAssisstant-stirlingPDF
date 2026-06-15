from __future__ import annotations

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from french_reader.markdown_pdf import markdown_to_reportlab_html, wrap_cjk_segments
from french_reader.pdf_fonts import FONT_LATIN, FONT_LATIN_BOLD, register_export_fonts
from french_reader.schemas import HistoryExportEntry

MODE_LABELS = {
    "translate": "Translation",
    "vocabulary": "Vocabulary",
    "grammar": "Grammar",
}
MODE_ORDER = ("translate", "vocabulary", "grammar")


def _entry_translations(entry: HistoryExportEntry) -> dict[str, str]:
    if entry.translations:
        return {key: value for key, value in entry.translations.items() if value}
    if entry.translation:
        mode = entry.translation_mode or "translate"
        return {mode: entry.translation}
    return {}


def _format_timestamp(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso


def _plain_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    lines = text.split("\n") or [""]
    parts = [escape(line) if line else "&nbsp;" for line in lines]
    html = "<br/>".join(parts)
    return Paragraph(wrap_cjk_segments(html), style)


def _markdown_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(markdown_to_reportlab_html(text), style)


def build_history_pdf(entries: list[HistoryExportEntry], source_file_name: str) -> bytes:
    if not entries:
        raise ValueError("No history entries to export")

    register_export_fonts()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="French Reading Assistant Notes",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ExportTitle",
        parent=styles["Heading1"],
        fontName=FONT_LATIN_BOLD,
        fontSize=16,
        leading=20,
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "ExportMeta",
        parent=styles["Normal"],
        fontName=FONT_LATIN,
        fontSize=9,
        leading=12,
        textColor="#666666",
        spaceAfter=8,
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName=FONT_LATIN_BOLD,
        fontSize=12,
        leading=16,
        spaceBefore=8,
        spaceAfter=4,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontName=FONT_LATIN_BOLD,
        fontSize=10,
        leading=14,
        spaceBefore=6,
        spaceAfter=2,
    )
    french_body_style = ParagraphStyle(
        "FrenchBody",
        parent=styles["Normal"],
        fontName=FONT_LATIN,
        fontSize=11,
        leading=15,
        spaceAfter=4,
    )
    notes_body_style = ParagraphStyle(
        "NotesBody",
        parent=styles["Normal"],
        fontName=FONT_LATIN,
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )

    exported_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = [
        Paragraph("French Reading Assistant Notes", title_style),
        Paragraph(
            f"Source: {escape(source_file_name)}<br/>Exported: {exported_at}",
            meta_style,
        ),
        HRFlowable(width="100%", thickness=0.5, color="#cccccc"),
        Spacer(1, 6),
    ]

    for index, entry in enumerate(entries, start=1):
        story.append(
            Paragraph(
                f"{index}. Page {entry.page} · {_format_timestamp(entry.created_at)}",
                section_style,
            )
        )
        story.append(Paragraph(escape(entry.file_name), meta_style))
        story.append(Paragraph("French", label_style))
        story.append(_plain_paragraph(entry.text, french_body_style))

        for mode in MODE_ORDER:
            text = _entry_translations(entry).get(mode)
            if not text:
                continue
            story.append(Paragraph(MODE_LABELS[mode], label_style))
            story.append(_markdown_paragraph(text, notes_body_style))

        if index < len(entries):
            story.extend(
                [
                    Spacer(1, 4),
                    HRFlowable(width="100%", thickness=0.5, color="#dddddd"),
                    Spacer(1, 4),
                ]
            )

    doc.build(story)
    return buffer.getvalue()
