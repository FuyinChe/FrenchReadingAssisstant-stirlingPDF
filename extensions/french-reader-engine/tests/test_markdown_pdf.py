from french_reader.export_service import build_history_pdf
from french_reader.markdown_pdf import markdown_to_reportlab_html, wrap_cjk_segments
from french_reader.schemas import HistoryExportEntry


def test_markdown_bold_converted_for_pdf():
    html = markdown_to_reportlab_html("• **bizarres** /bi.zaʁ/ — 奇怪的")
    assert "**" not in html
    assert "CharisSIL-Bold" in html
    assert "bizarres" in html
    assert "STSong-Light" in html
    assert "奇怪的" in html


def test_wrap_cjk_segments():
    html = wrap_cjk_segments("hello 你好 /bi.zaʁ/")
    assert "STSong-Light" in html
    assert "你好" in html
    assert "/bi.zaʁ/" in html


def test_markdown_preserves_line_breaks():
    html = markdown_to_reportlab_html("line one\nline two")
    assert "<br/>" in html
    assert "line one" in html
    assert "line two" in html


def test_build_history_pdf_with_markdown_vocabulary():
    entries = [
        HistoryExportEntry(
            id="1",
            created_at="2026-06-13T10:00:00",
            file_name="demo.pdf",
            page=2,
            text="Ils sont bizarres.",
            confidence=0.95,
            translations={
                "vocabulary": "• **bizarres** /bi.zaʁ/ — 奇怪的\n• **inquiets** /ɛ̃.kjɛ/ — 担心的",
            },
        )
    ]
    pdf = build_history_pdf(entries, "demo.pdf")
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500
