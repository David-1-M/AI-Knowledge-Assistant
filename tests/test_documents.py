
import pymupdf
from fastapi.testclient import TestClient

from app.main import app
from app.api import documents


client = TestClient(app)


def make_pdf(text: str) -> bytes:
    doc = pymupdf.open()

    page = doc.new_page()
    page.insert_text((72, 72), text)

    pdf_bytes = doc.tobytes()
    doc.close()

    return pdf_bytes


def test_upload_valid_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(
        documents, "UPLOAD_DIR", tmp_path
    )

    pdf_bytes = make_pdf(
        "Machine learning uses data."
    )

    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "notes.pdf",
                pdf_bytes,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["page_count"] == 1
    assert "Machine learning" in data["text"]

    saved_file = (
        tmp_path / f"{data['document_id']}.pdf"
    )

    assert saved_file.exists()


def test_reject_non_pdf():
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "notes.txt",
                b"Hello world",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400


def test_reject_invalid_pdf():
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "fake.pdf",
                b"Not a PDF",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400


def test_reject_oversized_pdf():
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "large.pdf",
                b"%PDF-" + b"x" * (10 * 1024 * 1024),
                "application/pdf"
            )
        }
    )

    assert response.status_code == 413


def test_reject_scanned_or_empty_pdf():
    doc = pymupdf.open()
    doc.new_page()

    pdf_bytes = doc.tobytes()
    doc.close()

    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "empty.pdf",
                pdf_bytes,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 422
