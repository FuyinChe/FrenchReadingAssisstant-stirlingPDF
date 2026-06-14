from fastapi.testclient import TestClient

from french_reader.export_service import build_history_pdf
from french_reader.main import app
from french_reader.schemas import HistoryExportEntry

client = TestClient(app)


def test_build_history_pdf_bytes():
    entries = [
        HistoryExportEntry(
            id="1",
            created_at="2026-06-13T10:00:00",
            file_name="demo.pdf",
            page=2,
            text="Bonjour le monde!",
            confidence=0.95,
            translations={"translate": "你好，世界！"},
        )
    ]
    pdf = build_history_pdf(entries, "demo.pdf")
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500


def test_build_history_pdf_requires_entries():
    try:
        build_history_pdf([], "demo.pdf")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "No history entries" in str(exc)


def test_export_pdf_endpoint():
    response = client.post(
        "/french-reader/export/pdf",
        json={
            "source_file_name": "demo.pdf",
            "entries": [
                {
                    "id": "1",
                    "created_at": "2026-06-13T10:00:00",
                    "file_name": "demo.pdf",
                    "page": 1,
                    "text": "Salut!",
                    "confidence": 0.9,
                    "translations": {"translate": "你好！"},
                }
            ],
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_export_pdf_rejects_empty_entries():
    response = client.post(
        "/french-reader/export/pdf",
        json={"source_file_name": "demo.pdf", "entries": []},
    )
    assert response.status_code == 422


def test_export_pdf_skips_blank_text_entries():
    response = client.post(
        "/french-reader/export/pdf",
        json={
            "source_file_name": "demo.pdf",
            "entries": [
                {
                    "id": "1",
                    "created_at": "2026-06-13T10:00:00",
                    "file_name": "demo.pdf",
                    "page": 1,
                    "text": "   ",
                    "confidence": 0.9,
                },
                {
                    "id": "2",
                    "created_at": "2026-06-13T10:00:00",
                    "file_name": "demo.pdf",
                    "page": 1,
                    "text": "Salut!",
                    "confidence": 95,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
